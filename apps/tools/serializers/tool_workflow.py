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
# coding=utf-8
import pickle
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

from application.flow.common import Workflow, WorkflowMode
from application.flow.i_step_node import ToolWorkflowPostHandler
from application.flow.tool_workflow_manage import ToolWorkflowManage
from application.models import ChatRecord
from application.serializers.application import McpServersSerializer, get_mcp_tools
from application.serializers.common import ToolExecute
from common.exception.app_exception import AppApiException
from common.field.common import UploadedFileField
from common.result import result
from common.utils.common import bytes_to_uploaded_file
from common.utils.common import restricted_loads, generate_uuid
from common.utils.logger import maxkb_logger
from common.utils.tool_code import ToolExecutor
from knowledge.models import KnowledgeWorkflow
from system_manage.models import AuthTargetType
from system_manage.serializers.user_resource_permission import UserResourcePermissionSerializer
from tools.models import Tool, ToolScope, ToolWorkflow, ToolWorkflowVersion
from tools.serializers.tool import ToolExportModelSerializer
from users.models import User

tool_executor = ToolExecutor()


def hand_node(node, update_tool_map):
    if node.get('type') == 'tool-lib-node':
        tool_lib_id = (node.get('properties', {}).get('node_data', {}).get('tool_lib_id') or '')
        node.get('properties', {}).get('node_data', {})['tool_lib_id'] = update_tool_map.get(tool_lib_id, tool_lib_id)

    if node.get('type') == 'search-knowledge-node':
        node.get('properties', {}).get('node_data', {})['knowledge_id_list'] = []
    if node.get('type') == 'ai-chat-node':
        node_data = node.get('properties', {}).get('node_data', {})
        mcp_tool_ids = node_data.get('mcp_tool_ids') or []
        node_data['mcp_tool_ids'] = [update_tool_map.get(tool_id,
                                                         tool_id) for tool_id in mcp_tool_ids]
        tool_ids = node_data.get('tool_ids') or []
        node_data['tool_ids'] = [update_tool_map.get(tool_id,
                                                     tool_id) for tool_id in tool_ids]
    if node.get('type') == 'mcp-node':
        mcp_tool_id = (node.get('properties', {}).get('node_data', {}).get('mcp_tool_id') or '')
        node.get('properties', {}).get('node_data', {})['mcp_tool_id'] = update_tool_map.get(mcp_tool_id,
                                                                                             mcp_tool_id)


class ToolWorkflowModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolWorkflow
        fields = '__all__'


class ToolWorkflowImportRequest(serializers.Serializer):
    file = UploadedFileField(required=True, label=_("file"))


class ToolWorkflowActionListQuerySerializer(serializers.Serializer):
    user_name = serializers.CharField(required=False, label=_('Name'), allow_blank=True, allow_null=True)
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
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        tool_id = serializers.UUIDField(required=True, label=_('tool id'))

        def debug(self, instance: Dict, user, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            tool_workflow = QuerySet(ToolWorkflow).filter(tool_id=self.data.get("tool_id")).first()
            tool_record_id = instance.get('chat_record_id') or str(uuid.uuid7())
            took_execute = ToolExecute(self.data.get("tool_id"), tool_record_id,
                                       self.data.get("workspace_id"),
                                       None,
                                       None,
                                       True)
            record = took_execute.get_record()
            work_flow_manage = ToolWorkflowManage(
                Workflow.new_instance(tool_workflow.work_flow, WorkflowMode.TOOL),
                {
                    'chat_record_id': tool_record_id,
                    'tool_id': self.data.get("tool_id"),
                    'stream': True,
                    'workspace_id': self.data.get("workspace_id"),
                    **instance},

                ToolWorkflowPostHandler(took_execute, self.data.get("tool_id")),
                is_the_task_interrupted=lambda: False,
                child_node=instance.get('child_node'),
                start_node_id=instance.get('runtime_node_id'),
                start_node_data=instance.get('node_data'),
                chat_record=self.to_chat_record(record)
            )

            r = work_flow_manage.run()
            return r

        @staticmethod
        def to_chat_record(record):
            if record is None:
                return None
            return ChatRecord(
                answer_text_list=record.meta.get('answer_text_list'),
                details=record.meta.get('details'),
                answer_text='',
            )

        def publish(self, with_valid=True):
            if with_valid:
                self.is_valid()
            user_id = self.data.get('user_id')
            workspace_id = self.data.get("workspace_id")
            user = QuerySet(User).filter(id=user_id).first()
            tool_workflow = QuerySet(ToolWorkflow).filter(tool_id=self.data.get("tool_id"),
                                                          workspace_id=workspace_id).first()
            work_flow_version = ToolWorkflowVersion(work_flow=tool_workflow.work_flow,
                                                    tool_id=self.data.get("tool_id"),
                                                    name=timezone.localtime(timezone.now()).strftime(
                                                        '%Y-%m-%d %H:%M:%S'),
                                                    publish_user_id=user_id,
                                                    publish_user_name=user.username,
                                                    workspace_id=workspace_id)
            work_flow_version.save()
            QuerySet(ToolWorkflow).filter(
                tool_id=self.data.get("tool_id")
            ).update(is_publish=True, publish_time=timezone.now())
            return True

        def edit(self, instance: Dict):
            self.is_valid(raise_exception=True)
            if instance.get("work_flow"):
                QuerySet(ToolWorkflow).update_or_create(tool_id=self.data.get("tool_id"),
                                                        create_defaults={'id': uuid.uuid7(),
                                                                         'tool_id': self.data.get(
                                                                             "tool_id"),
                                                                         "workspace_id": self.data.get(
                                                                             'workspace_id'),
                                                                         'work_flow': instance.get('work_flow',
                                                                                                   {}), },
                                                        defaults={
                                                            'tool_id': self.data.get("tool_id"),
                                                            'workspace_id': self.data.get(
                                                                'workspace_id'),
                                                            'work_flow': instance.get('work_flow')
                                                        })
                return self.one()
            if instance.get("work_flow_template"):
                template_instance = instance.get('work_flow_template')
                download_url = template_instance.get('downloadUrl')
                # 查找匹配的版本名称
                res = requests.get(download_url, timeout=5)
                ToolWorkflowSerializer.Import(data={
                    'user_id': self.data.get('user_id'),
                    'workspace_id': self.data.get('workspace_id'),
                    'tool_id': str(self.data.get('tool_id')),
                }).import_({'file': bytes_to_uploaded_file(res.content, 'file.tool')}, is_import_tool=False)

                try:
                    requests.get(template_instance.get('downloadCallbackUrl'), timeout=5)
                except Exception as e:
                    maxkb_logger.error(f"callback appstore tool download error: {e}")

                return self.one()

        def one(self):
            self.is_valid(raise_exception=True)
            workflow = QuerySet(ToolWorkflow).filter(tool_id=self.data.get('tool_id')).first()
            return {**ToolWorkflowModelSerializer(workflow).data}


class ToolWorkflowMcpSerializer(serializers.Serializer):
    tool_id = serializers.UUIDField(required=True, label=_('Tool id'))
    user_id = serializers.UUIDField(required=True, label=_("User ID"))
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        query_set = QuerySet(Tool).filter(id=self.data.get('tool_id'))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _('Tool id does not exist'))

    def get_mcp_servers(self, instance, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
            McpServersSerializer(data=instance).is_valid(raise_exception=True)
        servers = json.loads(instance.get('mcp_servers'))
        for server, config in servers.items():
            if config.get('transport') not in ['sse', 'streamable_http']:
                raise AppApiException(500, _('Only support transport=sse or transport=streamable_http'))
        tools = []
        for server in servers:
            tools += [
                {
                    'server': server,
                    'name': tool.name,
                    'description': tool.description,
                    'args_schema': tool.args_schema,
                }
                for tool in asyncio.run(get_mcp_tools({server: servers[server]}))]
        return tools
