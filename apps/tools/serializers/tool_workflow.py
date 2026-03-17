# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： tool_workflow.py
    @date：2026/3/6 13:59
    @desc:
"""
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
    class Import(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        workspace_id = serializers.CharField(required=False, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))

        @transaction.atomic
        def import_(self, instance: dict, is_import_tool, with_valid=True):
            if with_valid:
                self.is_valid()
                ToolWorkflowSerializer(data=instance).is_valid(raise_exception=True)
            user_id = self.data.get('user_id')
            workspace_id = self.data.get('workspace_id')
            tool_id = self.data.get('tool_id')
            tool_instance_bytes = instance.get('file').read()
            try:
                tool_instance = restricted_loads(tool_instance_bytes)
            except Exception as e:
                raise AppApiException(1001, _("Unsupported file format"))
            tool_workflow = tool_instance.work_flow
            tool_list = tool_instance.get_tool_list()
            update_tool_map = {}
            if len(tool_list) > 0:
                tool_id_list = reduce(lambda x, y: [*x, *y],
                                      [[tool.get('id'), generate_uuid((tool.get('id') + workspace_id or ''))]
                                       for tool
                                       in
                                       tool_list], [])
                # 存在的工具列表
                exits_tool_id_list = [str(tool.id) for tool in
                                      QuerySet(Tool).filter(id__in=tool_id_list, workspace_id=workspace_id)]
                # 需要更新的工具集合
                update_tool_map = {tool.get('id'): generate_uuid((tool.get('id') + workspace_id or '')) for tool
                                   in
                                   tool_list if
                                   not exits_tool_id_list.__contains__(
                                       tool.get('id'))}

                tool_list = [{**tool, 'id': update_tool_map.get(tool.get('id'))} for tool in tool_list if
                             not exits_tool_id_list.__contains__(
                                 tool.get('id')) and not exits_tool_id_list.__contains__(
                                 generate_uuid((tool.get('id') + workspace_id or '')))]

            work_flow = self.to_tool_workflow(
                tool_workflow,
                update_tool_map,
            )
            tool_model_list = [self.to_tool(tool, workspace_id, user_id) for tool in tool_list]
            QuerySet(ToolWorkflow).filter(workspace_id=workspace_id, tool_id=tool_id).update_or_create(
                tool_id=tool_id,
                workspace_id=workspace_id,
                defaults={'work_flow': work_flow}
            )

            if is_import_tool:
                if len(tool_model_list) > 0:
                    QuerySet(Tool).bulk_create(tool_model_list)
                    UserResourcePermissionSerializer(data={
                        'workspace_id': self.data.get('workspace_id'),
                        'user_id': self.data.get('user_id'),
                        'auth_target_type': AuthTargetType.TOOL.value
                    }).auth_resource_batch([t.id for t in tool_model_list])

        @staticmethod
        def to_tool_workflow(knowledge_workflow, update_tool_map):
            work_flow = knowledge_workflow.get("work_flow")
            for node in work_flow.get('nodes', []):
                hand_node(node, update_tool_map)
                if node.get('type') == 'loop_node':
                    for n in node.get('properties', {}).get('node_data', {}).get('loop_body', {}).get('nodes', []):
                        hand_node(n, update_tool_map)
            return work_flow

        @staticmethod
        def to_tool(tool, workspace_id, user_id):
            return Tool(id=tool.get('id'),
                        user_id=user_id,
                        name=tool.get('name'),
                        code=tool.get('code'),
                        template_id=tool.get('template_id'),
                        input_field_list=tool.get('input_field_list'),
                        init_field_list=tool.get('init_field_list'),
                        is_active=False if len((tool.get('init_field_list') or [])) > 0 else tool.get('is_active'),
                        tool_type=tool.get('tool_type', 'CUSTOM') or 'CUSTOM',
                        scope=ToolScope.SHARED if workspace_id == 'None' else ToolScope.WORKSPACE,
                        folder_id='default' if workspace_id == 'None' else workspace_id,
                        workspace_id=workspace_id)

    class Export(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        workspace_id = serializers.CharField(required=False, label=_('workspace id'))
        tool_id = serializers.UUIDField(required=True, label=_('knowledge id'))

        def export(self, with_valid=True):
            try:
                if with_valid:
                    self.is_valid()
                tool_id = self.data.get('tool_id')
                tool_workflow = QuerySet(ToolWorkflow).filter(tool_id=tool_id).first()
                tool = QuerySet(Tool).filter(id=tool_id).first()
                from application.flow.tools import get_tool_id_list
                tool_id_list = get_tool_id_list(tool_workflow.work_flow)
                tool_list = []
                if len(tool_id_list) > 0:
                    tool_list = QuerySet(Tool).filter(id__in=tool_id_list).exclude(scope=ToolScope.SHARED)
                tool_workflow_dict = {'id': tool.id,
                                      'work_flow': tool_workflow.work_flow,
                                      'workspace_id': tool.workspace_id,
                                      'name': tool.name,
                                      'desc': tool.desc,
                                      'tool_type': tool.tool_type}

                tool_workflow_instance = ToolWorkflowInstance(
                    tool_workflow_dict,
                    'v2',
                    [ToolExportModelSerializer(tool).data for tool in tool_list]
                )
                tool_workflow_pickle = pickle.dumps(tool_workflow_instance)
                response = HttpResponse(content_type='text/plain', content=tool_workflow_pickle)
                response['Content-Disposition'] = f'attachment; filename="{tool.name}.tool"'
                return response
            except Exception as e:
                return result.error(str(e), response_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            workflow = QuerySet(KnowledgeWorkflow).filter(knowledge_id=self.data.get('knowledge_id')).first()
            return {**ToolWorkflowModelSerializer(workflow).data}
