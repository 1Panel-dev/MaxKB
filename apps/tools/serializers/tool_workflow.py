# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： tool_workflow.py
@date：2026/3/6 13:59
@desc:
"""

import asyncio
import json
import os

# coding=utf-8
import pickle
import queue
import tempfile
import time
import zipfile
from functools import reduce
from typing import Dict, List

import requests
import uuid_utils.compat as uuid
from application.flow.tools import to_stream_response_simple
from application.workflow.common import WorkflowType, new_instance
from application.workflow.message.aggregator import AggregationManager
from application.workflow.nodes import get_node_class
from application.workflow.status import Status
from application.workflow.workflow_manage import CallBack, WorkflowManage
from application.serializers.application import (
    McpServersSerializer,
    get_mcp_tools,
    validate_bound_tool_permissions,
)
from common.constants.cache_version import Cache_Version
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.handle.impl.response.system_to_response import SystemToResponse
from common.exception.app_exception import AppApiException
from common.field.common import UploadedFileField
from common.result import result
from common.utils.common import bytes_to_uploaded_file, generate_uuid, restricted_loads
from common.utils.logger import maxkb_logger
from common.utils.tool_code import ToolExecutor
from common.utils.url_validator import ALLOWED_CALLBACK_HOSTS, ALLOWED_DOWNLOAD_HOSTS, validate_trusted_url
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q, QuerySet
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, gettext
from knowledge.models import Knowledge, KnowledgeScope, KnowledgeWorkflow
from knowledge.models.knowledge_action import State
from knowledge.serializers.knowledge import KnowledgeModelSerializer, KnowledgeSerializer
from maxkb.const import CONFIG
from rest_framework import serializers, status
from rest_framework.utils.formatting import lazy_format
from system_manage.models import AuthTargetType
from system_manage.models.resource_mapping import ResourceMapping
from system_manage.serializers.user_resource_permission import UserResourcePermissionSerializer
from users.models import User

from tools.models import Tool, ToolScope, ToolWorkflow, ToolWorkflowVersion
from tools.serializers.tool import ToolExportModelSerializer, ToolSerializer

tool_executor = ToolExecutor()


def is_valid_tool_workflow_circular_dependency(workflow, _id, visited=None, stack=None):
    """
    workflow: 当前要检查的 workflow 对象
    visited: 全局已经访问过的 workflow id
    stack: 当前递归栈里的 workflow id
    """
    if visited is None:
        visited = set()
    if stack is None:
        stack = set()

    if _id in stack:
        return False

    if _id in visited:
        return True

    stack.add(_id)

    for node in workflow.get("nodes", []):
        child_tool_ids = []
        if node.get("type") == "ai-chat-node":
            node_data = node.get("properties", {}).get("node_data", {})
            child_tool_ids = node_data.get("tool_ids") or []
        if node.get("type") == "tool-workflow-lib-node":
            child_tool_id = node.get("properties", {}).get("node_data", {}).get("tool_lib_id")
            child_tool_ids.append(child_tool_id)
        for child_tool_id in child_tool_ids:
            if child_tool_id:
                child_workflow = QuerySet(ToolWorkflow).filter(tool_id=child_tool_id).first()
                if child_workflow:
                    if not is_valid_tool_workflow_circular_dependency(
                        child_workflow.work_flow, str(child_tool_id), visited, stack
                    ):
                        return False

    stack.remove(_id)
    visited.add(_id)
    return True


def hand_node(node, update_tool_map):
    if node.get("type") == "tool-lib-node":
        tool_lib_id = node.get("properties", {}).get("node_data", {}).get("tool_lib_id") or ""
        node.get("properties", {}).get("node_data", {})["tool_lib_id"] = update_tool_map.get(tool_lib_id, tool_lib_id)

    if node.get("type") == "search-knowledge-node":
        node.get("properties", {}).get("node_data", {})["knowledge_id_list"] = []
    if node.get("type") == "ai-chat-node":
        node_data = node.get("properties", {}).get("node_data", {})
        mcp_tool_ids = node_data.get("mcp_tool_ids") or []
        node_data["mcp_tool_ids"] = [update_tool_map.get(tool_id, tool_id) for tool_id in mcp_tool_ids]
        tool_ids = node_data.get("tool_ids") or []
        node_data["tool_ids"] = [update_tool_map.get(tool_id, tool_id) for tool_id in tool_ids]
    if node.get("type") == "mcp-node":
        mcp_tool_id = node.get("properties", {}).get("node_data", {}).get("mcp_tool_id") or ""
        node.get("properties", {}).get("node_data", {})["mcp_tool_id"] = update_tool_map.get(mcp_tool_id, mcp_tool_id)


class ToolWorkflowModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolWorkflow
        fields = "__all__"


class ToolWorkflowImportRequest(serializers.Serializer):
    file = UploadedFileField(required=True, label=_("file"))


class ToolWorkflowActionListQuerySerializer(serializers.Serializer):
    user_name = serializers.CharField(required=False, label=_("Name"), allow_blank=True, allow_null=True)
    state = serializers.CharField(required=False, label=_("State"), allow_blank=True, allow_null=True)


class ToolWorkflowInstance:
    def __init__(self, knowledge_workflow: dict, version: str, tool_list: List[dict]):
        self.knowledge_workflow = knowledge_workflow
        self.version = version
        self.tool_list = tool_list

    def get_tool_list(self):
        return self.tool_list or []


class ToolWorkflowSerializer(serializers.Serializer):
    class Operate(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_("user id"))
        workspace_id = serializers.CharField(required=False, label=_("workspace id"), allow_blank=True, allow_null=True)
        tool_id = serializers.UUIDField(required=True, label=_("tool id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get("workspace_id")
            query_set = QuerySet(Tool).filter(id=self.data.get("tool_id"))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _("Tool id does not exist"))

        def debug(self, instance: Dict, user, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            tool_workflow = QuerySet(ToolWorkflow).filter(tool_id=self.data.get("tool_id")).first()
            workspace_id = tool_workflow.workspace_id
            tool_record_id = instance.get("chat_record_id") or str(uuid.uuid7())
            # 表单节点等断点续跑:position 指向要从其恢复执行的节点,机制与 chat 一致
            position = instance.get("position")
            # 运行身份取自认证上下文(DB 工作空间 + 登录用户),请求体不得覆盖,
            # 防止低权限用户伪造 workspace_id/user_id 绕过工具引用授权;
            # chat_record_id 仅用于沿用同一条执行记录,工具工作流本身不作为运行参数
            identity_keys = {"workspace_id", "user_id", "chat_user_id", "chat_user_type", "chat_record_id"}
            # 对齐旧引擎 get_body():输入字段值 + 执行身份,不含对话语义字段(question/chat_record_id)
            parameters = {
                "tool_id": self.data.get("tool_id"),
                "stream": True,
                "debug": True,
                "workspace_id": workspace_id,
                "user_id": self.data.get("user_id"),
                **{k: v for k, v in instance.items() if k not in identity_keys},
            }

            workflow = new_instance(tool_workflow.work_flow, WorkflowType.TOOL)
            aggregation = AggregationManager()
            result_queue = queue.Queue()
            base_to_response = SystemToResponse()
            start_time = time.time()

            def on_next(wf_manage, content):
                aggregation.aggregate(content)
                result_queue.put(("chunk", content.to_dict()))

            def on_complete(wf_manage, error):
                try:
                    self.save_tool_record(
                        tool_record_id,
                        self.data.get("tool_id"),
                        workspace_id,
                        wf_manage,
                        aggregation,
                        parameters,
                        start_time,
                        error,
                        position,
                    )
                finally:
                    result_queue.put(("error", error) if error else ("done", None))

            call_back = CallBack(on_next, on_complete)

            def get_node_parameters(node):
                return node.properties.get("node_data", {})

            def get_start_node_fn(wf, wm):
                # 有 position:从指定节点续跑(表单节点等),与 chat 的 position 机制一致
                if position and position.get("id"):
                    node = wf.get_node(position.get("id"))
                    if node:
                        node_class = get_node_class(node.type, WorkflowType.TOOL)
                        return node_class(node, wm, get_node_parameters)
                # 默认从工具起始节点开始
                start_node = wf.get_node("tool-start-node")
                if start_node is None:
                    raise AppApiException(500, gettext("The start node does not exist"))
                node_class = get_node_class(start_node.type, WorkflowType.TOOL)
                return node_class(start_node, wm, get_node_parameters)

            # 有 position 且有记录 id:从历史 context 恢复(position 机制与 chat 一致);恢复失败回退为全新执行。
            # 工具无 ChatRecord,context 来源是 debug 专用缓存——通过 get_context 回调提供,from_context 只负责重建
            if position and instance.get("chat_record_id"):

                def get_tool_context():
                    return cache.get(Cache_Version.DEBUG_WORKFLOW_CONTEXT.get_key(chat_record_id=str(tool_record_id)))

                work_flow_manage = WorkflowManage.from_context(
                    get_context=get_tool_context,
                    workflow=workflow,
                    parameters=parameters,
                    workflow_type=WorkflowType.TOOL,
                    call_back=call_back,
                    get_start_node=get_start_node_fn,
                )
                if work_flow_manage is None:
                    work_flow_manage = WorkflowManage(
                        workflow, parameters, WorkflowType.TOOL, call_back, get_start_node_fn
                    )
            else:
                work_flow_manage = WorkflowManage(workflow, parameters, WorkflowType.TOOL, call_back, get_start_node_fn)
            work_flow_manage.start_node.workflow_manage = work_flow_manage

            def generate():
                work_flow_manage.run()
                while True:
                    msg_type, data = result_queue.get()
                    if msg_type == "done":
                        yield "data: [DONE]\n\n"
                        break
                    if msg_type == "error":
                        error_block = {"id": str(uuid.uuid7()), "type": "FAILURE", "content": str(data)}
                        frame = base_to_response.to_stream(tool_record_id, tool_record_id, error_block)
                        if frame is not None:
                            yield "data: " + frame + "\n\n"
                        yield "data: [DONE]\n\n"
                        break
                    if msg_type == "chunk":
                        frame = base_to_response.to_stream(tool_record_id, tool_record_id, data)
                        if frame is not None:
                            yield "data: " + frame + "\n\n"

            return to_stream_response_simple(generate())

        @staticmethod
        def save_tool_record(
            tool_record_id, tool_id, workspace_id, wf_manage, aggregation, parameters, start_time, error, position=None
        ):
            """
            工具调试执行结束后写执行记录缓存(替代旧引擎 ToolWorkflowPostHandler)。
            debug 只写 30 分钟 Redis 缓存、不落库,前端据此拉取 meta.output/details 展示;
            缓存 shape 与 tool 记录查询端点(ToolSerializer...one)读取的字段保持一致。
            同时把运行 context 写入 DEBUG_WORKFLOW_CONTEXT,供下次 position 续跑时 from_context 恢复。
            """
            workflow = wf_manage.workflow
            base_node = workflow.get_node("tool-base-node")
            input_field_list = base_node.properties.get("user_input_field_list", []) if base_node else []
            output_field_list = base_node.properties.get("user_output_field_list", []) if base_node else []
            input_data = {f.get("field"): parameters.get(f.get("field")) for f in input_field_list}
            # 新引擎工具输出收口于全局 output 上下文(tool-start-node 初始化、变量赋值节点写入)
            output = wf_manage.context.get("output", {})
            # 续跑(有 position):合并上一次的节点详情,与 chat 的 get_details 用法一致
            old_details = None
            if position:
                prev_record = cache.get(
                    Cache_Version.TOOL_WORKFLOW_EXECUTE.get_key(key=tool_record_id),
                    version=Cache_Version.TOOL_WORKFLOW_EXECUTE.get_version(),
                )
                if prev_record:
                    old_details = (prev_record.get("meta") or {}).get("details")
            details = wf_manage.get_details(position=position, old_details=old_details)
            tool_record = {
                "id": tool_record_id,
                "tool_id": tool_id,
                "workspace_id": workspace_id,
                "source_type": None,
                "source_id": None,
                "state": ToolWorkflowSerializer.Operate.compute_tool_state(details, error),
                "run_time": time.time() - start_time,
                "meta": {
                    "input_field_list": input_field_list,
                    "output_field_list": output_field_list,
                    "input": input_data,
                    "output": output,
                    "details": details,
                    "answer_text_list": aggregation.get_contents(),
                },
            }
            cache.set(
                Cache_Version.TOOL_WORKFLOW_EXECUTE.get_key(key=tool_record_id),
                tool_record,
                version=Cache_Version.TOOL_WORKFLOW_EXECUTE.get_version(),
                timeout=60 * 30,
            )
            # 持久化运行 context,供 position 续跑时恢复(工具无 ChatRecord,故写 debug 专用缓存)。
            # 读写都用 cache.get/set(key) 不带 version,两侧须一致,否则 Django version 命名空间对不上会命中不到。
            cache.set(
                Cache_Version.DEBUG_WORKFLOW_CONTEXT.get_key(chat_record_id=str(tool_record_id)),
                wf_manage.context,
                timeout=60 * 30,
            )

        @staticmethod
        def compute_tool_state(details, error):
            if error:
                return State.FAILURE
            has_fail = any((d or {}).get("status") == Status.FAIL.value for d in (details or []))
            return State.FAILURE if has_fail else State.SUCCESS

        def publish(self, with_valid=True):
            if with_valid:
                self.is_valid()
            user_id = self.data.get("user_id")

            user = QuerySet(User).filter(id=user_id).first()
            tool_workflow = QuerySet(ToolWorkflow).filter(tool_id=self.data.get("tool_id")).first()
            workspace_id = tool_workflow.workspace_id
            work_flow_version = ToolWorkflowVersion(
                work_flow=tool_workflow.work_flow,
                tool_id=self.data.get("tool_id"),
                name=timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S"),
                publish_user_id=user_id,
                publish_user_name=user.username,
                workspace_id=workspace_id,
            )
            work_flow_version.save()
            QuerySet(ToolWorkflow).filter(tool_id=self.data.get("tool_id")).update(
                is_publish=True, publish_time=timezone.now()
            )
            return True

        def list_knowledge(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            workspace_id = self.data.get("workspace_id")
            user_id = self.data.get("user_id")
            if workspace_id == "None":
                return [
                    {**KnowledgeModelSerializer(k).data, "scope": "SHARED"}
                    for k in QuerySet(Knowledge).filter(workspace_id="None")
                ]
            knowledge_workspace_authorization_model = DatabaseModelManage.get_model("knowledge_workspace_authorization")
            share_knowledge_list = []
            if knowledge_workspace_authorization_model is not None:
                white_list_condition = Q(authentication_type="WHITE_LIST") & Q(
                    workspace_id_list__contains=[workspace_id]
                )
                default_condition = ~Q(authentication_type="WHITE_LIST") & ~Q(
                    workspace_id_list__contains=[workspace_id]
                )
                # 组合查询
                query = white_list_condition | default_condition
                inner = QuerySet(knowledge_workspace_authorization_model).filter(query)
                share_knowledge_list = [
                    {**KnowledgeModelSerializer(k).data, "scope": "SHARED"}
                    for k in QuerySet(Knowledge).filter(id__in=inner)
                ]
            workspace_knowledge_list = [
                {**k, "scope": "WORKSPACE"}
                for k in KnowledgeSerializer.Query(
                    data={"workspace_id": workspace_id, "scope": KnowledgeScope.WORKSPACE, "user_id": user_id}
                ).list()
                if k.get("resource_type") == "knowledge"
            ]

            return [*workspace_knowledge_list, *share_knowledge_list]

        @staticmethod
        def get_tool_knowledge_mapping(application_knowledge_id_list, knowledge_id_list, tool_id):
            """

            @param application_knowledge_id_list:  当前应用可修改的知识库列表
            @param knowledge_id_list:              用户修改的知识库列表
            @param application_id:                 应用id
            @return:
            """
            # 当前知识库和应用已关联列表
            knowledge_application_mapping_list = (
                QuerySet(ResourceMapping)
                .filter(
                    source_id=tool_id,
                    source_type="TOOL",
                    target_type="KNOWLEDGE",
                )
                .exclude(target_id__in=application_knowledge_id_list)
            )
            edit_knowledge_list = [
                ResourceMapping(source_id=tool_id, target_id=knowledge_id, source_type="TOOL", target_type="KNOWLEDGE")
                for knowledge_id in knowledge_id_list
            ]
            return list(knowledge_application_mapping_list) + edit_knowledge_list

        def edit(self, instance: Dict):
            self.is_valid(raise_exception=True)
            tool = QuerySet(Tool).filter(id=self.data.get("tool_id")).first()
            workflow_id = tool.workspace_id
            if instance.get("work_flow"):
                # 校验工作流中引用的工具(mcp-node 的 mcp_tool_id 等)当前用户是否有权使用,
                # 防止低权限用户绑定他人工具并通过工作流执行绕过工具的单独授权控制
                validate_bound_tool_permissions(self.data.get("user_id"), workflow_id, instance)
                dependency = is_valid_tool_workflow_circular_dependency(
                    workflow=instance.get("work_flow"), _id=str(tool.id)
                )
                if not dependency:
                    raise Exception(gettext("There is a circular dependency in the tool workflow"))
                QuerySet(ToolWorkflow).update_or_create(
                    tool_id=self.data.get("tool_id"),
                    create_defaults={
                        "id": uuid.uuid7(),
                        "tool_id": self.data.get("tool_id"),
                        "workspace_id": workflow_id,
                        "work_flow": instance.get("work_flow", {}),
                    },
                    defaults={
                        "tool_id": self.data.get("tool_id"),
                        "workspace_id": workflow_id,
                        "work_flow": instance.get("work_flow"),
                    },
                )
                # 当前用户可修改关联的知识库列表
                tool_knowledge_id_list = [
                    str(knowledge.get("id"))
                    for knowledge in ToolWorkflowSerializer.Operate(
                        data={
                            "user_id": self.data.get("user_id"),
                            "tool_id": self.data.get("tool_id"),
                            "workspace_id": workflow_id,
                        }
                    ).list_knowledge()
                ]
                knowledge_id_list = []
                if "knowledge_id_list" in instance:
                    # 当前用户可修改关联的知识库列表
                    application_knowledge_id_list = [
                        str(knowledge.get("id"))
                        for knowledge in ToolWorkflowSerializer.Operate(
                            data={
                                "user_id": self.data.get("user_id"),
                                "tool_id": self.data.get("tool_id"),
                                "workspace_id": workflow_id,
                            }
                        ).list_knowledge()
                    ]
                    knowledge_id_list = instance.get("knowledge_id_list")
                    for knowledge_id in knowledge_id_list:
                        if not application_knowledge_id_list.__contains__(knowledge_id):
                            message = lazy_format(
                                _("Unknown knowledge base id {dataset_id}, unable to associate"),
                                dataset_id=knowledge_id,
                            )
                            raise AppApiException(500, str(message))

                update_resource_mapping_by_tool(
                    self.data.get("tool_id"),
                    self.get_tool_knowledge_mapping(
                        tool_knowledge_id_list, knowledge_id_list, self.data.get("tool_id")
                    ),
                )
                return self.one()
            if instance.get("work_flow_template"):
                template_instance = instance.get("work_flow_template")
                download_url = template_instance.get("downloadUrl")
                if not validate_trusted_url(download_url, ALLOWED_DOWNLOAD_HOSTS):
                    raise AppApiException(500, _("Illegal download url"))
                # 查找匹配的版本名称
                res = requests.get(download_url, timeout=5, allow_redirects=False)
                tool = QuerySet(Tool).filter(id=self.data.get("tool_id")).first()
                ToolSerializer.Import(
                    data={
                        "user_id": self.data.get("user_id"),
                        "workspace_id": workflow_id,
                        "folder_id": tool.folder_id,
                        "file": bytes_to_uploaded_file(res.content, "file.tool"),
                    }
                ).update_template_workflow(str(self.data.get("tool_id")))

                try:
                    download_callback_url = template_instance.get("downloadCallbackUrl", "")
                    if not validate_trusted_url(download_callback_url, ALLOWED_CALLBACK_HOSTS):
                        raise AppApiException(500, _("Illegal download callback url"))
                    requests.get(download_callback_url, timeout=5, allow_redirects=False)
                except Exception as e:
                    maxkb_logger.error(f"callback appstore tool download error: {e}")

                return self.one()

        def one(self):
            self.is_valid(raise_exception=True)
            workflow = QuerySet(ToolWorkflow).filter(tool_id=self.data.get("tool_id")).first()
            return {**ToolWorkflowModelSerializer(workflow).data}


class ToolWorkflowMcpSerializer(serializers.Serializer):
    tool_id = serializers.UUIDField(required=True, label=_("Tool id"))
    user_id = serializers.UUIDField(required=True, label=_("User ID"))
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get("workspace_id")
        query_set = QuerySet(Tool).filter(id=self.data.get("tool_id"))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _("Tool id does not exist"))

    def get_mcp_servers(self, instance, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            McpServersSerializer(data=instance).is_valid(raise_exception=True)
        servers = json.loads(instance.get("mcp_servers"))
        for server, config in servers.items():
            if config.get("transport") not in ["sse", "streamable_http"]:
                raise AppApiException(500, _("Only support transport=sse or transport=streamable_http"))
        tools = []
        for server in servers:
            tools += [
                {
                    "server": server,
                    "name": tool.name,
                    "description": tool.description,
                    "args_schema": tool.args_schema,
                }
                for tool in asyncio.run(get_mcp_tools({server: servers[server]}))
            ]
        return tools


class StoreToolWorkflow(serializers.Serializer):
    user_id = serializers.UUIDField(required=True, label=_("User ID"))
    name = serializers.CharField(required=False, label=_("tool name"), allow_null=True, allow_blank=True)

    def get_appstore_templates(self):
        self.is_valid(raise_exception=True)
        # 下载zip文件
        try:
            appstore_url = CONFIG.get("APPSTORE_URL", "https://apps-assets.fit2cloud.com/stable/maxkb.json.zip")
            res = requests.get(appstore_url, timeout=5)
            res.raise_for_status()
            # 创建临时文件保存zip
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
                temp_zip.write(res.content)
                temp_zip_path = temp_zip.name

            try:
                # 解压zip文件
                with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
                    # 获取zip中的第一个文件（假设只有一个json文件）
                    json_filename = zip_ref.namelist()[0]
                    json_content = zip_ref.read(json_filename)

                # 将json转换为字典
                tool_store = json.loads(json_content.decode("utf-8"))
                tag_dict = {tag["name"]: tag["key"] for tag in tool_store["additionalProperties"]["tags"]}
                filter_apps = []
                for tool in tool_store["apps"]:
                    if self.data.get("name", "") != "":
                        if self.data.get("name").lower() not in tool.get("name", "").lower():
                            continue
                    if not tool["downloadUrl"].endswith(".tool") or not [
                        tag_dict[tag] for tag in tool.get("tags")
                    ].__contains__("workflow_template"):
                        continue
                    versions = tool.get("versions", [])
                    tool["label"] = tag_dict[tool.get("tags")[0]] if tool.get("tags") else ""
                    tool["version"] = next(
                        (
                            version.get("name")
                            for version in versions
                            if version.get("downloadUrl") == tool["downloadUrl"]
                        ),
                    )
                    filter_apps.append(tool)

                tool_store["apps"] = filter_apps
                return tool_store
            finally:
                # 清理临时文件
                os.unlink(temp_zip_path)
        except Exception as e:
            maxkb_logger.error(f"fetch appstore tools error: {e}")
            return {"apps": [], "additionalProperties": {"tags": []}}


def update_resource_mapping_by_tool(tool_id: str, other_resource_mapping=None):
    from application.flow.tools import get_instance_resource, save_workflow_mapping
    from system_manage.models.resource_mapping import ResourceType

    if other_resource_mapping is None:
        other_resource_mapping = []
    tool = QuerySet(ToolWorkflow).filter(tool_id=tool_id).first()
    instance_mapping = get_instance_resource(tool, ResourceType.TOOL, str(tool_id), {})
    save_workflow_mapping(tool.work_flow, ResourceType.TOOL, str(tool_id), instance_mapping + other_resource_mapping)

    return
