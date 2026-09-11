# coding=utf-8
import asyncio
import base64
import json
import pickle
import time
from copy import deepcopy
from functools import reduce
from typing import Dict, List

import requests
import uuid_utils.compat as uuid
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

from application.workflow.common import WorkflowType, new_instance
from application.workflow.i_node import Signal
from application.workflow.nodes import get_node_class
from system_manage.services.resource_mapping import get_tool_id_list, save_workflow_mapping
from application.workflow.status import Status
from application.workflow.workflow_manage import CallBack, WorkflowManage
from application.workflow.workflow_run_registry import WorkflowRunRegistry
from application.mcp_tools import get_mcp_tools
from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.field.common import UploadedFileField
from common.result import result
from common.utils.common import bytes_to_uploaded_file
from common.utils.common import restricted_loads, generate_uuid
from common.utils.logger import maxkb_logger
from common.utils.rsa_util import rsa_long_decrypt
from common.utils.tool_code import ToolExecutor
from common.utils.url_validator import ALLOWED_CALLBACK_HOSTS, ALLOWED_DOWNLOAD_HOSTS, validate_trusted_url
from knowledge.models import (
    KnowledgeScope,
    Knowledge,
    KnowledgeType,
    KnowledgeWorkflow,
    KnowledgeWorkflowVersion,
    File,
    FileSourceType,
    Document,
    DocumentResourceType,
    KnowledgeSyncLog,
    KnowledgeSyncStatus,
    KnowledgeSyncType,
)
from knowledge.models.knowledge_action import KnowledgeAction, State
from knowledge.serializers.common import update_resource_mapping_by_knowledge
from knowledge.serializers.knowledge_model import KnowledgeModelSerializer
from knowledge.services.document_cleanup import delete_document_data
from knowledge.services.workflow_sync import merge_workflow_incremental_snapshot
from system_manage.models import AuthTargetType
from system_manage.models.resource_mapping import ResourceType
from system_manage.serializers.user_resource_permission import UserResourcePermissionSerializer
from tools.models import Tool, ToolScope, ToolType, ToolWorkflow
from tools.serializers.tool import ToolExportModelSerializer
from users.models import User

tool_executor = ToolExecutor()


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

        skill_tool_ids = node_data.get("skill_tool_ids") or []
        node_data["skill_tool_ids"] = [update_tool_map.get(tool_id, tool_id) for tool_id in skill_tool_ids]
    if node.get("type") == "mcp-node":
        mcp_tool_id = node.get("properties", {}).get("node_data", {}).get("mcp_tool_id") or ""
        node.get("properties", {}).get("node_data", {})["mcp_tool_id"] = update_tool_map.get(mcp_tool_id, mcp_tool_id)
    if node.get("type") == "tool-workflow-lib-node":
        tool_lib_id = node.get("properties", {}).get("node_data", {}).get("tool_lib_id") or ""
        node.get("properties", {}).get("node_data", {})["tool_lib_id"] = update_tool_map.get(tool_lib_id, tool_lib_id)


def finalize_knowledge_action(knowledge_action_id, state, run_time, sync_log_id=None, document_cleanup=None):
    """
    知识库工作流执行结束后的收尾:更新 KnowledgeAction 的最终状态/耗时,并在同步场景下收尾 KnowledgeSyncLog。
    与具体执行引擎解耦——state/run_time 由调用方按各自引擎算好传入。
    """
    QuerySet(KnowledgeAction).filter(id=knowledge_action_id).update(state=state, run_time=run_time)
    if sync_log_id is not None:
        sync_log = QuerySet(KnowledgeSyncLog).filter(id=sync_log_id).first()
        if sync_log is not None:
            if (
                state == State.SUCCESS
                and sync_log.sync_type == KnowledgeSyncType.INCREMENTAL
                and document_cleanup is not None
            ):
                stats = merge_workflow_incremental_snapshot(sync_log)
            else:
                stats = {
                    "total_count": QuerySet(Document)
                    .filter(
                        knowledge_id=sync_log.knowledge_id,
                        resource_type=DocumentResourceType.DOCUMENT,
                    )
                    .count(),
                    "synced_count": QuerySet(Document)
                    .filter(
                        knowledge_id=sync_log.knowledge_id,
                        type=KnowledgeType.WORKFLOW,
                        resource_type=DocumentResourceType.DOCUMENT,
                        create_time__gte=sync_log.create_time,
                    )
                    .count(),
                    "skipped_count": 0,
                    "deleted_count": sync_log.deleted_count,
                    "failed_count": 0 if state == State.SUCCESS else 1,
                }
            is_success = state == State.SUCCESS
            QuerySet(KnowledgeSyncLog).filter(id=sync_log.id).update(
                status=KnowledgeSyncStatus.SUCCESS
                if is_success and not stats["failed_count"]
                else KnowledgeSyncStatus.FAILURE,
                total_count=stats["total_count"],
                synced_count=stats["synced_count"],
                skipped_count=stats["skipped_count"],
                deleted_count=stats["deleted_count"],
                failed_count=stats["failed_count"],
                duration_ms=max(0, round(run_time * 1000)),
                message=f"Workflow action {knowledge_action_id}: {state}",
            )


class KnowledgeWorkflowModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeWorkflow
        fields = "__all__"


class KnowledgeWorkflowActionRequestSerializer(serializers.Serializer):
    data_source = serializers.DictField(required=True, label=_("datasource data"))
    knowledge_base = serializers.DictField(required=True, label=_("knowledge base data"))


class KnowledgeWorkflowImportRequest(serializers.Serializer):
    file = UploadedFileField(required=True, label=_("file"))


class KnowledgeWorkflowActionListQuerySerializer(serializers.Serializer):
    user_name = serializers.CharField(required=False, label=_("Name"), allow_blank=True, allow_null=True)
    state = serializers.CharField(required=False, label=_("State"), allow_blank=True, allow_null=True)


class KBWFInstance:
    def __init__(self, knowledge_workflow: dict, function_lib_list: List[dict], version: str, tool_list: List[dict]):
        self.knowledge_workflow = knowledge_workflow
        self.function_lib_list = function_lib_list
        self.version = version
        self.tool_list = tool_list

    def get_tool_list(self):
        return [*(self.tool_list or []), *(self.function_lib_list or [])]


class KnowledgeWorkflowActionSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_("workspace id"))
    knowledge_id = serializers.UUIDField(required=True, label=_("knowledge id"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get("workspace_id")
        query_set = QuerySet(Knowledge).filter(id=self.data.get("knowledge_id"))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _("Knowledge id does not exist"))

    def get_query_set(self, instance: Dict):
        query_set = (
            QuerySet(KnowledgeAction)
            .filter(knowledge_id=self.data.get("knowledge_id"))
            .values("id", "knowledge_id", "state", "meta", "run_time", "create_time")
        )
        if instance.get("user_name"):
            query_set = query_set.filter(meta__user_name__icontains=instance.get("user_name"))
        if instance.get("state"):
            query_set = query_set.filter(state=instance.get("state"))
        return query_set.order_by("-create_time")

    def list(self, instance: Dict, is_valid=True):
        if is_valid:
            self.is_valid(raise_exception=True)
            KnowledgeWorkflowActionListQuerySerializer(data=instance).is_valid(raise_exception=True)
        return [
            {
                "id": a.get("id"),
                "knowledge_id": a.get("knowledge_id"),
                "state": a.get("state"),
                "meta": a.get("meta"),
                "run_time": a.get("run_time"),
                "create_time": a.get("create_time"),
            }
            for a in self.get_query_set(instance)
        ]

    def page(self, current_page, page_size, instance: Dict, is_valid=True):
        if is_valid:
            self.is_valid(raise_exception=True)
            KnowledgeWorkflowActionListQuerySerializer(data=instance).is_valid(raise_exception=True)
        return page_search(
            current_page,
            page_size,
            self.get_query_set(instance),
            lambda a: {
                "id": a.get("id"),
                "knowledge_id": a.get("knowledge_id"),
                "state": a.get("state"),
                "meta": a.get("meta"),
                "run_time": a.get("run_time"),
                "create_time": a.get("create_time"),
            },
        )

    def action(self, instance: Dict, user, with_valid=True, sync_log_id=None):
        if with_valid:
            self.is_valid(raise_exception=True)
        knowledge_workflow = QuerySet(KnowledgeWorkflow).filter(knowledge_id=self.data.get("knowledge_id")).first()
        knowledge_action_id = uuid.uuid7()
        meta = {"user_id": str(user.id), "user_name": user.username}
        KnowledgeAction(
            id=knowledge_action_id, knowledge_id=self.data.get("knowledge_id"), state=State.STARTED, meta=meta
        ).save()
        knowledge = QuerySet(Knowledge).filter(id=self.data.get("knowledge_id")).first()
        if sync_log_id is None:
            knowledge.meta = {
                **(knowledge.meta or {}),
                "workflow_sync_input": {
                    "data_source": deepcopy(instance.get("data_source") or {}),
                    "knowledge_base": deepcopy(instance.get("knowledge_base") or {}),
                },
            }
            knowledge.save(update_fields=["meta", "update_time"])
        instance["knowledge_base"] = {
            **(instance.get("knowledge_base") or {}),
            "knowledge": {
                "id": str(knowledge.id),
                "name": knowledge.name,
                "desc": knowledge.desc,
                "workspace_id": knowledge.workspace_id,
            },
        }
        self._launch_knowledge_workflow(instance, user, knowledge_action_id, knowledge_workflow.work_flow, sync_log_id)
        # 需要把文件改成永久文件
        data_source = instance.get("data_source") or {}
        file_ids = [item.get("file_id") for item in data_source.get("file_list") or [] if item.get("file_id")]
        knowledge_id = str(self.data.get("knowledge_id"))
        file_list = list(QuerySet(File).filter(id__in=file_ids))
        for file in file_list:
            meta = dict(file.meta or {})
            meta.update(debug=False, knowledge_id=knowledge_id)
            file.source_type = FileSourceType.KNOWLEDGE.value
            file.source_id = knowledge_id
            file.meta = meta
        QuerySet(File).bulk_update(file_list, ["source_type", "source_id", "meta"])
        return {
            "id": knowledge_action_id,
            "knowledge_id": self.data.get("knowledge_id"),
            "state": State.STARTED,
            "details": {},
            "meta": meta,
        }

    def _launch_knowledge_workflow(self, instance: Dict, user, knowledge_action_id, work_flow, sync_log_id=None):
        """
        在新引擎上异步启动知识库工作流(action/upload_document 共用):
        动态解析数据源起点 -> 注册到运行注册表(供停止)-> run() 每节点起线程立即返回,
        最终状态由 on_complete 通过 finalize_knowledge_action 落库。
        """
        parameters = {
            "knowledge_id": self.data.get("knowledge_id"),
            "knowledge_action_id": knowledge_action_id,
            "stream": True,
            "workspace_id": self.data.get("workspace_id"),
            "user_id": str(user.id),
            **instance,
        }
        workflow = new_instance(work_flow, WorkflowType.KNOWLEDGE)
        start_time = time.time()

        def get_node_parameters(node):
            return node.properties.get("node_data", {})

        def get_start_node_fn(wf, wm):
            # 知识库起点是数据源节点,由 data_source.node_id 指定(动态,非固定 start-node)
            node_id = (instance.get("data_source") or {}).get("node_id")
            node = wf.get_node(node_id) if node_id else None
            if node is None:
                raise AppApiException(500, _("The start node does not exist"))
            return get_node_class(node.type, WorkflowType.KNOWLEDGE)(node, wm, get_node_parameters)

        def on_next(wf_manage, content):
            # 实时刷新节点详情,供前端轮询 KnowledgeAction 展示进度
            QuerySet(KnowledgeAction).filter(id=knowledge_action_id).update(details=wf_manage.get_details())

        def on_complete(wf_manage, error):
            WorkflowRunRegistry.unregister(str(knowledge_action_id))
            details = wf_manage.get_details()
            cancelled = wf_manage.signal == Signal.CANCELLED
            state = self.compute_knowledge_state(details, error, cancelled)
            run_time = time.time() - start_time
            QuerySet(KnowledgeAction).filter(id=knowledge_action_id).update(details=details)
            finalize_knowledge_action(knowledge_action_id, state, run_time, sync_log_id, delete_document_data)

        call_back = CallBack(on_next, on_complete)
        work_flow_manage = WorkflowManage(workflow, parameters, WorkflowType.KNOWLEDGE, call_back, get_start_node_fn)
        WorkflowRunRegistry.register(str(knowledge_action_id), None, work_flow_manage)
        work_flow_manage.run()
        return work_flow_manage

    @staticmethod
    def compute_knowledge_state(details, error, cancelled):
        if cancelled:
            return State.REVOKED
        details = details or []
        has_fail = any(d.get("status") == Status.FAIL.value and not d.get("enableException") for d in details)
        if error or has_fail:
            return State.FAILURE
        write_exist = any(d.get("type") == "knowledge-write-node" for d in details)
        if not write_exist:
            return State.FAILURE
        return State.SUCCESS

    def upload_document(self, instance: Dict, user, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        knowledge_workflow = QuerySet(KnowledgeWorkflow).filter(knowledge_id=self.data.get("knowledge_id")).first()
        if not knowledge_workflow.is_publish:
            raise AppApiException(500, _("The knowledge base workflow has not been published"))
        knowledge_workflow_version = (
            QuerySet(KnowledgeWorkflowVersion)
            .filter(knowledge_id=self.data.get("knowledge_id"))
            .order_by("-create_time")[0:1]
            .first()
        )
        knowledge_action_id = uuid.uuid7()
        meta = {"user_id": str(user.id), "user_name": user.username}
        KnowledgeAction(
            id=knowledge_action_id, knowledge_id=self.data.get("knowledge_id"), state=State.STARTED, meta=meta
        ).save()
        knowledge = QuerySet(Knowledge).filter(id=self.data.get("knowledge_id")).first()
        instance["knowledge_base"] = {
            **(instance.get("knowledge_base") or {}),
            "knowledge": {
                "id": str(knowledge.id),
                "name": knowledge.name,
                "desc": knowledge.desc,
                "workspace_id": knowledge.workspace_id,
            },
        }
        # 线上上传走已发布版本的 work_flow,执行链路与 action 一致(新引擎异步执行)
        self._launch_knowledge_workflow(instance, user, knowledge_action_id, knowledge_workflow_version.work_flow)
        return {
            "id": knowledge_action_id,
            "knowledge_id": self.data.get("knowledge_id"),
            "state": State.STARTED,
            "details": {},
            "meta": meta,
        }

    class Operate(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_("workspace id"))
        knowledge_id = serializers.UUIDField(required=True, label=_("knowledge id"))
        id = serializers.UUIDField(required=True, label=_("knowledge action id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get("workspace_id")
            query_set = QuerySet(Knowledge).filter(id=self.data.get("knowledge_id"))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _("Knowledge id does not exist"))
            if (
                not QuerySet(KnowledgeAction)
                .filter(id=self.data.get("id"), knowledge_id=self.data.get("knowledge_id"))
                .exists()
            ):
                raise AppApiException(500, _("Knowledge action does not exist"))

        def one(self, is_valid=True):
            if is_valid:
                self.is_valid(raise_exception=True)
            knowledge_action_id = self.data.get("id")
            knowledge_action = (
                QuerySet(KnowledgeAction)
                .filter(id=knowledge_action_id, knowledge_id=self.data.get("knowledge_id"))
                .first()
            )
            return {
                "id": knowledge_action_id,
                "knowledge_id": knowledge_action.knowledge_id,
                "state": knowledge_action.state,
                "details": knowledge_action.details,
                "meta": knowledge_action.meta,
            }

        def cancel(self, is_valid=True):
            if is_valid:
                self.is_valid(raise_exception=True)
            knowledge_action_id = self.data.get("id")
            # action / upload_document 均在新引擎执行,统一向运行注册表发送停止信号
            WorkflowRunRegistry.cancel_by_record_id(str(knowledge_action_id))
            QuerySet(KnowledgeAction).filter(
                id=knowledge_action_id,
                knowledge_id=self.data.get("knowledge_id"),
                state__in=[State.STARTED, State.PENDING],
            ).update(state=State.REVOKE)
            return True


class KnowledgeWorkflowSerializer(serializers.Serializer):
    class Datasource(serializers.Serializer):
        type = serializers.CharField(required=True, label=_("type"))
        id = serializers.CharField(required=True, label=_("type"))
        params = serializers.DictField(required=True, label="")
        function_name = serializers.CharField(required=True, label=_("function_name"))

        def action(self):
            self.is_valid(raise_exception=True)
            if self.data.get("type") == "local":
                # self.data["id"] 为数据源节点类型,取新引擎该节点类上的同名静态方法(如 get_form_list)
                node_class = get_node_class(self.data.get("id"), WorkflowType.KNOWLEDGE)
                return getattr(node_class, self.data.get("function_name"))(**self.data.get("params"))
            elif self.data.get("type") == "tool":
                tool = QuerySet(Tool).filter(id=self.data.get("id")).first()
                init_params = json.loads(rsa_long_decrypt(tool.init_params))
                return tool_executor.exec_code(
                    tool.code, {**init_params, **self.data.get("params")}, self.data.get("function_name")
                )

    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_("user id"))
        workspace_id = serializers.CharField(required=True, label=_("workspace id"))
        scope = serializers.ChoiceField(
            required=False, label=_("scope"), default=KnowledgeScope.WORKSPACE, choices=KnowledgeScope.choices
        )

        @transaction.atomic
        def save_workflow(self, instance: Dict):
            self.is_valid(raise_exception=True)

            folder_id = instance.get("folder_id", self.data.get("workspace_id"))

            knowledge_id = uuid.uuid7()
            knowledge = Knowledge(
                id=knowledge_id,
                name=instance.get("name"),
                desc=instance.get("desc"),
                user_id=self.data.get("user_id"),
                type=instance.get("type", KnowledgeType.WORKFLOW),
                scope=self.data.get("scope", KnowledgeScope.WORKSPACE),
                folder_id=folder_id,
                workspace_id=self.data.get("workspace_id"),
                embedding_model_id=instance.get("embedding_model_id"),
                meta={},
            )
            knowledge.save()
            # 自动资源给授权当前用户
            UserResourcePermissionSerializer(
                data={
                    "workspace_id": self.data.get("workspace_id"),
                    "user_id": self.data.get("user_id"),
                    "auth_target_type": AuthTargetType.KNOWLEDGE.value,
                }
            ).auth_resource(str(knowledge_id))

            knowledge_workflow = KnowledgeWorkflow(
                id=uuid.uuid7(),
                knowledge_id=knowledge_id,
                workspace_id=self.data.get("workspace_id"),
                work_flow=instance.get("work_flow", {}),
            )

            knowledge_workflow.save()
            save_workflow_mapping(instance.get("work_flow", {}), ResourceType.KNOWLEDGE, str(knowledge_id))

            # 处理 work_flow_template
            if instance.get("work_flow_template") is not None:
                template_instance = instance.get("work_flow_template")
                download_url = template_instance.get("downloadUrl")
                if not validate_trusted_url(download_url, ALLOWED_DOWNLOAD_HOSTS):
                    raise AppApiException(500, _("Illegal download url"))
                # 查找匹配的版本名称
                res = requests.get(download_url, timeout=5, allow_redirects=False)
                KnowledgeWorkflowSerializer.Import(
                    data={
                        "user_id": self.data.get("user_id"),
                        "workspace_id": self.data.get("workspace_id"),
                        "knowledge_id": str(knowledge_id),
                    }
                ).import_({"file": bytes_to_uploaded_file(res.content, "file.kbwf")}, is_import_tool=True)

                try:
                    download_callback_url = template_instance.get("downloadCallbackUrl", "")
                    if not validate_trusted_url(download_callback_url, ALLOWED_CALLBACK_HOSTS):
                        raise AppApiException(500, _("Illegal download callback url"))
                    requests.get(download_callback_url, timeout=5, allow_redirects=False)
                except Exception as e:
                    maxkb_logger.error(f"callback appstore tool download error: {e}")

            return {**KnowledgeModelSerializer(knowledge).data, "document_list": []}

    class Import(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_("user id"))
        workspace_id = serializers.CharField(required=False, label=_("workspace id"))
        knowledge_id = serializers.UUIDField(required=True, label=_("knowledge id"))

        @transaction.atomic
        def import_(self, instance: dict, is_import_tool, with_valid=True):
            if with_valid:
                self.is_valid()
                KnowledgeWorkflowImportRequest(data=instance).is_valid(raise_exception=True)
            user_id = self.data.get("user_id")
            workspace_id = self.data.get("workspace_id")
            knowledge_id = self.data.get("knowledge_id")
            kbwf_instance_bytes = instance.get("file").read()
            try:
                kbwf_instance = restricted_loads(kbwf_instance_bytes)
            except Exception:
                raise AppApiException(1001, _("Unsupported file format"))
            knowledge_workflow = kbwf_instance.knowledge_workflow
            tool_list = kbwf_instance.get_tool_list()
            update_tool_map = {}
            if len(tool_list) > 0:
                tool_id_list = reduce(
                    lambda x, y: [*x, *y],
                    [[tool.get("id"), generate_uuid((tool.get("id") + workspace_id or ""))] for tool in tool_list],
                    [],
                )
                # 存在的工具列表
                exits_tool_id_list = [
                    str(tool.id) for tool in QuerySet(Tool).filter(id__in=tool_id_list, workspace_id=workspace_id)
                ]
                # 需要更新的工具集合
                update_tool_map = {
                    tool.get("id"): generate_uuid((tool.get("id") + workspace_id or ""))
                    for tool in tool_list
                    if not exits_tool_id_list.__contains__(tool.get("id"))
                }

                tool_list = [
                    {**tool, "id": update_tool_map.get(tool.get("id"))}
                    for tool in tool_list
                    if not exits_tool_id_list.__contains__(tool.get("id"))
                    and not exits_tool_id_list.__contains__(generate_uuid((tool.get("id") + workspace_id or "")))
                ]

            work_flow = self.to_knowledge_workflow(
                knowledge_workflow,
                update_tool_map,
            )
            tool_model_list = [self.to_tool(tool, workspace_id, user_id) for tool in tool_list]
            KnowledgeWorkflow.objects.filter(workspace_id=workspace_id, knowledge_id=knowledge_id).update_or_create(
                knowledge_id=knowledge_id, workspace_id=workspace_id, defaults={"work_flow": work_flow}
            )

            if is_import_tool:
                if len(tool_model_list) > 0:
                    QuerySet(Tool).bulk_create(tool_model_list)
                    QuerySet(ToolWorkflow).bulk_create(
                        [
                            ToolWorkflow(
                                workspace_id=workspace_id,
                                work_flow=self.reset_workflow(tool.get("work_flow"), update_tool_map),
                                tool_id=tool.get("id"),
                            )
                            for tool in tool_list
                            if tool.get("tool_type") == ToolType.WORKFLOW
                        ]
                    )
                    UserResourcePermissionSerializer(
                        data={
                            "workspace_id": self.data.get("workspace_id"),
                            "user_id": self.data.get("user_id"),
                            "auth_target_type": AuthTargetType.TOOL.value,
                        }
                    ).auth_resource_batch([t.id for t in tool_model_list])
                return True
            update_resource_mapping_by_knowledge(knowledge_id)

        @staticmethod
        def to_knowledge_workflow(knowledge_workflow, update_tool_map):
            work_flow = knowledge_workflow.get("work_flow")
            for node in work_flow.get("nodes", []):
                hand_node(node, update_tool_map)
                if node.get("type") == "loop-node":
                    for n in node.get("properties", {}).get("node_data", {}).get("loop_body", {}).get("nodes", []):
                        hand_node(n, update_tool_map)
            return work_flow

        @staticmethod
        def reset_workflow(work_flow, update_tool_map):
            for node in work_flow.get("nodes", []):
                hand_node(node, update_tool_map)
                if node.get("type") == "loop-node":
                    for n in node.get("properties", {}).get("node_data", {}).get("loop_body", {}).get("nodes", []):
                        hand_node(n, update_tool_map)
            return work_flow

        @staticmethod
        def to_tool(tool, workspace_id, user_id):
            # 如果是技能类型的工具，需要将code保存为文件
            code = tool.get("code")
            if tool.get("tool_type") == ToolType.SKILL:
                skill_file_id = uuid.uuid7()
                skill_file = File(
                    id=skill_file_id,
                    file_name=f"{tool.get('name')}.zip",
                    source_type=FileSourceType.TOOL,
                    source_id=tool.get("id"),
                    meta={},
                )
                skill_file.save(base64.b64decode(code))
                tool["code"] = skill_file_id
            return Tool(
                id=tool.get("id"),
                user_id=user_id,
                name=tool.get("name"),
                code=tool.get("code"),
                template_id=tool.get("template_id"),
                input_field_list=tool.get("input_field_list"),
                init_field_list=tool.get("init_field_list"),
                is_active=False if len((tool.get("init_field_list") or [])) > 0 else tool.get("is_active"),
                tool_type=tool.get("tool_type", "CUSTOM") or "CUSTOM",
                scope=ToolScope.SHARED if workspace_id == "None" else ToolScope.WORKSPACE,
                folder_id="default" if workspace_id == "None" else workspace_id,
                workspace_id=workspace_id,
            )

    class Export(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_("user id"))
        workspace_id = serializers.CharField(required=False, label=_("workspace id"))
        knowledge_id = serializers.UUIDField(required=True, label=_("knowledge id"))

        def export(self, with_valid=True):
            try:
                if with_valid:
                    self.is_valid()
                knowledge_id = self.data.get("knowledge_id")
                knowledge_workflow = QuerySet(KnowledgeWorkflow).filter(knowledge_id=knowledge_id).first()
                knowledge = QuerySet(Knowledge).filter(id=knowledge_id).first()
                tool_id_list = get_tool_id_list(knowledge_workflow.work_flow, True)
                tool_list = []
                if len(tool_id_list) > 0:
                    tool_list = QuerySet(Tool).filter(id__in=tool_id_list).exclude(scope=ToolScope.SHARED)
                tw_dict = {
                    tw.tool_id: tw
                    for tw in QuerySet(ToolWorkflow).filter(
                        tool_id__in=[tool.id for tool in tool_list if tool.tool_type == ToolType.WORKFLOW]
                    )
                }

                # 如果是技能工具，则需要将code字段转换为文件内容的base64字符串
                for tool in tool_list:
                    if tool.tool_type == ToolType.SKILL:
                        skill_file = QuerySet(File).filter(id=tool.code).first()
                        if skill_file:
                            tool.code = base64.b64encode(skill_file.get_bytes()).decode("utf-8")

                knowledge_workflow_dict = KnowledgeWorkflowModelSerializer(knowledge_workflow).data

                kbwf_instance = KBWFInstance(
                    knowledge_workflow_dict, [], "v2", [self.to_tool_dict(tool, tw_dict) for tool in tool_list]
                )
                knowledge_workflow_pickle = pickle.dumps(kbwf_instance)
                response = HttpResponse(content_type="text/plain", content=knowledge_workflow_pickle)
                response["Content-Disposition"] = f'attachment; filename="{knowledge.name}.kbwf"'
                return response
            except Exception as e:
                return result.error(str(e), response_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        @staticmethod
        def to_tool_dict(tool, tool_workflow_dict):
            if tool.tool_type == ToolType.WORKFLOW:
                return {**ToolExportModelSerializer(tool).data, "work_flow": tool_workflow_dict.get(tool.id).work_flow}
            return ToolExportModelSerializer(tool).data

    class Operate(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_("user id"))
        workspace_id = serializers.CharField(required=True, label=_("workspace id"))
        knowledge_id = serializers.UUIDField(required=True, label=_("knowledge id"))

        def publish(self, with_valid=True):
            if with_valid:
                self.is_valid()
            user_id = self.data.get("user_id")
            workspace_id = self.data.get("workspace_id")
            user = QuerySet(User).filter(id=user_id).first()
            knowledge_workflow = (
                QuerySet(KnowledgeWorkflow)
                .filter(knowledge_id=self.data.get("knowledge_id"), workspace_id=workspace_id)
                .first()
            )
            work_flow_version = KnowledgeWorkflowVersion(
                work_flow=knowledge_workflow.work_flow,
                knowledge_id=self.data.get("knowledge_id"),
                name=timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S"),
                publish_user_id=user_id,
                publish_user_name=user.username,
                workspace_id=workspace_id,
            )
            work_flow_version.save()
            QuerySet(KnowledgeWorkflow).filter(knowledge_id=self.data.get("knowledge_id")).update(
                is_publish=True, publish_time=timezone.now()
            )
            return True

        def edit(self, instance: Dict):
            self.is_valid(raise_exception=True)
            if instance.get("work_flow"):
                QuerySet(KnowledgeWorkflow).update_or_create(
                    knowledge_id=self.data.get("knowledge_id"),
                    create_defaults={
                        "id": uuid.uuid7(),
                        "knowledge_id": self.data.get("knowledge_id"),
                        "workspace_id": self.data.get("workspace_id"),
                        "work_flow": instance.get("work_flow", {}),
                    },
                    defaults={"work_flow": instance.get("work_flow")},
                )
                update_resource_mapping_by_knowledge(self.data.get("knowledge_id"))
                return self.one()
            if instance.get("work_flow_template"):
                template_instance = instance.get("work_flow_template")
                download_url = template_instance.get("downloadUrl")
                if not validate_trusted_url(download_url, ALLOWED_DOWNLOAD_HOSTS):
                    raise AppApiException(500, _("Illegal download url"))
                # 查找匹配的版本名称
                res = requests.get(download_url, timeout=5, allow_redirects=False)
                KnowledgeWorkflowSerializer.Import(
                    data={
                        "user_id": self.data.get("user_id"),
                        "workspace_id": self.data.get("workspace_id"),
                        "knowledge_id": str(self.data.get("knowledge_id")),
                    }
                ).import_({"file": bytes_to_uploaded_file(res.content, "file.kbwf")}, is_import_tool=False)

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
            workflow = QuerySet(KnowledgeWorkflow).filter(knowledge_id=self.data.get("knowledge_id")).first()
            return {**KnowledgeWorkflowModelSerializer(workflow).data}


class McpServersSerializer(serializers.Serializer):
    mcp_servers = serializers.JSONField(required=True)


class KnowledgeWorkflowMcpSerializer(serializers.Serializer):
    knowledge_id = serializers.UUIDField(required=True, label=_("knowledge id"))
    user_id = serializers.UUIDField(required=True, label=_("User ID"))
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get("workspace_id")
        query_set = QuerySet(Knowledge).filter(id=self.data.get("knowledge_id"))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _("Knowledge id does not exist"))

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
