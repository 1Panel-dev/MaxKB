# -*- coding: utf-8 -*-
"""
导入(应用 / 知识库工作流 / 工具工作流)时,包内工具的复用、新建与引用权限校验
"""

from typing import Dict, List, Tuple

import uuid_utils.compat as uuid
from common.exception.app_exception import AppApiException
from common.utils.common import generate_uuid
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework.utils.formatting import lazy_format
from system_manage.models import AuthTargetType, WorkspaceUserResourcePermission
from tools.models import Tool
from users.serializers.user import is_workspace_manage


def _walk_workflow_nodes(work_flow, collector):
    """遍历工作流节点(含 loop-node 嵌套),对每个节点的 node_data 调用 collector。"""
    if not work_flow:
        return
    for node in work_flow.get("nodes", []) or []:
        node_data = (node.get("properties") or {}).get("node_data") or {}
        collector(node_data)
        if node.get("type") == "loop-node":
            _walk_workflow_nodes(node_data.get("loop_body"), collector)


def get_bound_tool_ids(instance: Dict) -> List[str]:
    """
    收集应用配置(含工作流节点)中引用的所有工具id,用于绑定前的权限校验
    """
    tool_ids = set()
    for key in ("tool_ids", "skill_tool_ids", "mcp_tool_ids"):
        for tool_id in instance.get(key) or []:
            tool_ids.add(str(tool_id))
    if instance.get("mcp_tool_id"):
        tool_ids.add(str(instance.get("mcp_tool_id")))

    def collect(node_data):
        for key in ("tool_lib_id", "mcp_tool_id"):
            if node_data.get(key):
                tool_ids.add(str(node_data.get(key)))
        for key in ("mcp_tool_ids", "tool_ids", "skill_tool_ids"):
            for tool_id in node_data.get(key) or []:
                tool_ids.add(str(tool_id))

    _walk_workflow_nodes(instance.get("work_flow"), collect)
    return list(tool_ids)


def get_authorized_tool_ids(user_id: str, workspace_id: str, tool_ids: List[str]) -> List[str]:
    """
    返回 tool_ids 中当前用户被授权绑定/使用的工具id。
    工作空间管理员默认拥有全部工具权限;其他用户必须在 workspace_user_resource_permission
    中存在针对该工具的显式授权记录(默认拒绝)。
    """
    if not tool_ids:
        return []
    tool_ids = list({str(t) for t in tool_ids})
    if is_workspace_manage(user_id, workspace_id):
        return tool_ids
    granted_tool_ids = {
        str(permission.target)
        for permission in QuerySet(WorkspaceUserResourcePermission).filter(
            workspace_id=workspace_id,
            user_id=user_id,
            auth_target_type=AuthTargetType.TOOL.value,
            target__in=tool_ids,
        )
        if "VIEW" in permission.permission_list or "ROLE" in permission.permission_list
    }
    return [tool_id for tool_id in tool_ids if tool_id in granted_tool_ids]


def resolve_import_tools(tool_list: List[Dict], workspace_id: str, user_id: str, force_new=False) -> Tuple[Dict, List]:
    """
    处理导入包内的工具:工作空间已存在且导入者有权限的直接复用,否则以新id新建

    @param tool_list:     导入包内的工具列表
    @param workspace_id:  工作空间id
    @param user_id:       导入者id
    @param force_new:     是否全部新建,不复用已存在的工具
    @return: (update_tool_map, new_tool_list)
             update_tool_map: 包内旧id -> 实际绑定id(复用的已存在id 或 新建id),用于改写工作流引用
             new_tool_list:   需要新建的工具,id 已替换为新id
    """
    tool_list = [tool for tool in {str(t.get("id")): t for t in tool_list if t.get("id")}.values()]
    if len(tool_list) == 0:
        return {}, []

    # 旧id -> 候选的已存在id(优先旧id本身,其次历史导入生成的确定性id)
    candidate_map = {}
    if not force_new:
        candidate_id_map = {
            str(tool.get("id")): [str(tool.get("id")), str(generate_uuid(str(tool.get("id")) + str(workspace_id)))]
            for tool in tool_list
        }
        exists_tool_id_set = {
            str(tool.id)
            for tool in QuerySet(Tool).filter(
                id__in=[i for ids in candidate_id_map.values() for i in ids], workspace_id=workspace_id
            )
        }
        authorized_tool_id_set = set(get_authorized_tool_ids(user_id, workspace_id, list(exists_tool_id_set)))
        for old_id, candidate_ids in candidate_id_map.items():
            existing_id = next((i for i in candidate_ids if i in exists_tool_id_set), None)
            if existing_id is not None and existing_id in authorized_tool_id_set:
                candidate_map[old_id] = existing_id

    update_tool_map = {}
    new_tool_list = []
    for tool in tool_list:
        old_id = str(tool.get("id"))
        if old_id in candidate_map:
            update_tool_map[old_id] = candidate_map[old_id]
        else:
            new_id = str(uuid.uuid7())
            update_tool_map[old_id] = new_id
            new_tool_list.append({**tool, "id": new_id})
    return update_tool_map, new_tool_list


def validate_unpackaged_tool_refs(instance_list: List[Dict], update_tool_map: Dict, user_id: str, workspace_id: str):
    """
    校验不在导入包内的工具引用:无法随包新建,只能绑定已存在的工具,需导入者有使用权限

    @param instance_list:   含工具引用的配置(应用 / 工作流 / 新建的工作流工具),须为改写引用前的原始数据
    @param update_tool_map: resolve_import_tools 返回的 id 映射
    """
    tool_ids = {tool_id for instance in instance_list for tool_id in get_bound_tool_ids(instance)}
    unpackaged_tool_ids = [tool_id for tool_id in tool_ids if tool_id not in update_tool_map]
    if not unpackaged_tool_ids:
        return
    authorized_tool_ids = set(get_authorized_tool_ids(user_id, workspace_id, unpackaged_tool_ids))
    unauthorized_tool_ids = [tool_id for tool_id in unpackaged_tool_ids if tool_id not in authorized_tool_ids]
    if unauthorized_tool_ids:
        message = lazy_format(_("No permission to use tool(s): {tool_ids}"), tool_ids=", ".join(unauthorized_tool_ids))
        raise AppApiException(403, str(message))
