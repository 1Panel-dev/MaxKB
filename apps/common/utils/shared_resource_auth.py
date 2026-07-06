"""
    @project: MaxKB-xpack-ee
    @Author: niu
    @file: shared_resource_auth.py
    @date: 2026/3/11 11:22
    @desc:
"""
from typing import List

from django.db.models import QuerySet

from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppApiException, AppUnauthorizedFailed
from knowledge.models import Knowledge
from system_manage.models import AuthTargetType, WorkspaceUserResourcePermission
from tools.models import Tool
from users.serializers.user import is_workspace_manage


def get_runtime_user_id(user_id=None, chat_user_id=None, chat_user_type=None):
    if user_id:
        return str(user_id)
    if chat_user_type == "PLATFORM_USER" and chat_user_id:
        return str(chat_user_id)
    return None


def _filter_user_authorized_tool_ids(ids: List[str], workspace_id: str, user_id=None) -> List[str]:
    if not ids or user_id is None or is_workspace_manage(user_id, workspace_id):
        return [str(i) for i in ids]
    permission_list = QuerySet(WorkspaceUserResourcePermission).filter(
        workspace_id=workspace_id,
        user_id=user_id,
        auth_target_type=AuthTargetType.TOOL.value,
        target__in=ids,
    )
    authorized_ids = {str(permission.target) for permission in permission_list if permission.permission_list}
    return [str(i) for i in ids if str(i) in authorized_ids]


def filter_authorized_ids(resource_type: str, ids: List[str], workspace_id: str, user_id=None) -> List[str]:
    """
    通用授权过滤函数

    @param resource_type: 资源类型 ('model', 'tool', 'knowledge')
    @param ids: 待过滤的ID列表
    @param workspace_id: 工作空间ID
    @param user_id: 当前工作空间用户ID（仅 tool 类型会按用户级授权进一步过滤）
    @return: 授权通过的ID列表
    """

    if not ids:
        return []

    auth_func = DatabaseModelManage.get_model(f"get_authorized_{resource_type}")

    model_class = {'tool': Tool, 'knowledge': Knowledge}.get(resource_type)
    if model_class is None:
        return ids

    same_workspace_ids = list(
        QuerySet(model_class).filter(id__in=ids, workspace_id=workspace_id)
        .values_list('id', flat=True)
    )

    cross_workspace_ids = [i for i in ids if i not in set(map(str, same_workspace_ids))]

    authorized_ids = set(map(str, same_workspace_ids))

    if cross_workspace_ids and auth_func is not None:
        cross_queryset = QuerySet(model_class).filter(id__in=cross_workspace_ids)
        authorized = auth_func(cross_queryset, workspace_id)
        authorized_ids.update(str(r.id) for r in authorized)

    if resource_type == "tool":
        authorized_ids = set(_filter_user_authorized_tool_ids(list(authorized_ids), workspace_id, user_id))

    return [i for i in ids if str(i) in authorized_ids]


def validate_authorized_tool_ids(tool_ids: List[str], workspace_id: str, user_id=None, extra_authorized_ids=None):
    normalized_tool_ids = [str(tool_id) for tool_id in tool_ids if tool_id]
    if not normalized_tool_ids:
        return []

    extra_authorized_set = {str(tool_id) for tool_id in (extra_authorized_ids or []) if tool_id}
    visible_ids = set(filter_authorized_ids("tool", normalized_tool_ids, workspace_id)) | extra_authorized_set
    if any(tool_id not in visible_ids for tool_id in normalized_tool_ids):
        raise AppApiException(500, "Tool id does not exist")

    if user_id is None:
        return normalized_tool_ids

    authorized_ids = set(filter_authorized_ids("tool", normalized_tool_ids, workspace_id, user_id=user_id))
    authorized_ids.update(extra_authorized_set)
    if any(tool_id not in authorized_ids for tool_id in normalized_tool_ids):
        raise AppUnauthorizedFailed(403, "No permission to access")
    return normalized_tool_ids