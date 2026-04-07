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
import tempfile
import zipfile
from functools import reduce
from typing import Dict, List

import requests
import uuid_utils.compat as uuid
from django.db import transaction
from django.db.models import QuerySet, Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from rest_framework.utils.formatting import lazy_format

from application.flow.common import Workflow, WorkflowMode
from application.flow.i_step_node import ToolWorkflowPostHandler
from application.flow.tool_workflow_manage import ToolWorkflowManage
from application.models import ChatRecord
from application.serializers.application import McpServersSerializer, get_mcp_tools
from application.serializers.common import ToolExecute
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppApiException
from common.field.common import UploadedFileField
from common.result import result
from common.utils.common import bytes_to_uploaded_file
from common.utils.common import restricted_loads, generate_uuid
from common.utils.logger import maxkb_logger
from common.utils.tool_code import ToolExecutor
from knowledge.models import KnowledgeWorkflow, Knowledge, KnowledgeScope
from knowledge.serializers.knowledge import KnowledgeModelSerializer, KnowledgeSerializer
from system_manage.models import AuthTargetType
from system_manage.models.resource_mapping import ResourceMapping
from system_manage.serializers.user_resource_permission import UserResourcePermissionSerializer
from tools.models import Tool, ToolScope, ToolWorkflow, ToolWorkflowVersion
from tools.serializers.tool import ToolExportModelSerializer, ToolSerializer
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
        workspace_id = serializers.CharField(required=False, label=_('workspace id'))
        tool_id = serializers.UUIDField(required=True, label=_('tool id'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Tool).filter(id=self.data.get('tool_id'))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Tool id does not exist'))

        def debug(self, instance: Dict, user, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            tool_workflow = QuerySet(ToolWorkflow).filter(tool_id=self.data.get("tool_id")).first()
            workspace_id = tool_workflow.workspace_id
            tool_record_id = instance.get('chat_record_id') or str(uuid.uuid7())
            took_execute = ToolExecute(self.data.get("tool_id"), tool_record_id,
                                       workspace_id,
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
                    'workspace_id': workspace_id,
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

            user = QuerySet(User).filter(id=user_id).first()
            tool_workflow = QuerySet(ToolWorkflow).filter(tool_id=self.data.get("tool_id")).first()
            workspace_id = tool_workflow.workspace_id
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

        def list_knowledge(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            workspace_id = self.data.get("workspace_id")
            user_id = self.data.get('user_id')
            if workspace_id == 'None':
                return [{**KnowledgeModelSerializer(k).data, 'scope': 'SHARED'} for k in
                        QuerySet(Knowledge).filter(workspace_id='None')]
            knowledge_workspace_authorization_model = DatabaseModelManage.get_model('knowledge_workspace_authorization')
            share_knowledge_list = []
            if knowledge_workspace_authorization_model is not None:
                white_list_condition = Q(authentication_type='WHITE_LIST') & Q(
                    workspace_id_list__contains=[workspace_id])
                default_condition = ~Q(authentication_type='WHITE_LIST') & ~Q(
                    workspace_id_list__contains=[workspace_id])
                # 组合查询
                query = white_list_condition | default_condition
                inner = QuerySet(knowledge_workspace_authorization_model).filter(query)
                share_knowledge_list = [{**KnowledgeModelSerializer(k).data, 'scope': 'SHARED'} for k in
                                        QuerySet(Knowledge).filter(id__in=inner)]
            workspace_knowledge_list = [{**k, 'scope': 'WORKSPACE'} for k in KnowledgeSerializer.Query(
                data={
                    'workspace_id': workspace_id,
                    'scope': KnowledgeScope.WORKSPACE,
                    'user_id': user_id
                }
            ).list() if k.get('resource_type') == 'knowledge']

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
            knowledge_application_mapping_list = QuerySet(ResourceMapping).filter(source_id=tool_id,
                                                                                  source_type='TOOL',
                                                                                  target_type="KNOWLEDGE",
                                                                                  ).exclude(
                target_id__in=application_knowledge_id_list)
            edit_knowledge_list = [ResourceMapping(source_id=tool_id, target_id=knowledge_id,
                                                   source_type='TOOL',
                                                   target_type="KNOWLEDGE")
                                   for knowledge_id in knowledge_id_list]
            return list(knowledge_application_mapping_list) + edit_knowledge_list

        def edit(self, instance: Dict):
            self.is_valid(raise_exception=True)
            tool = QuerySet(Tool).filter(id=self.data.get("tool_id")).first()
            workflow_id = tool.workspace_id
            if instance.get("work_flow"):
                QuerySet(ToolWorkflow).update_or_create(tool_id=self.data.get("tool_id"),
                                                        create_defaults={'id': uuid.uuid7(),
                                                                         'tool_id': self.data.get(
                                                                             "tool_id"),
                                                                         "workspace_id": workflow_id,
                                                                         'work_flow': instance.get('work_flow',
                                                                                                   {}), },
                                                        defaults={
                                                            'tool_id': self.data.get("tool_id"),
                                                            'workspace_id': workflow_id,
                                                            'work_flow': instance.get('work_flow')
                                                        })
                # 当前用户可修改关联的知识库列表
                tool_knowledge_id_list = [str(knowledge.get('id')) for knowledge in
                                          self.list_knowledge(with_valid=False)]
                knowledge_id_list = []
                if 'knowledge_id_list' in instance:
                    # 当前用户可修改关联的知识库列表
                    application_knowledge_id_list = [str(knowledge.get('id')) for knowledge in
                                                     self.list_knowledge(with_valid=False)]
                    knowledge_id_list = instance.get('knowledge_id_list')
                    for knowledge_id in knowledge_id_list:
                        if not application_knowledge_id_list.__contains__(knowledge_id):
                            message = lazy_format(_('Unknown knowledge base id {dataset_id}, unable to associate'),
                                                  dataset_id=knowledge_id)
                            raise AppApiException(500, str(message))

                update_resource_mapping_by_tool(self.data.get("tool_id"),
                                                self.get_tool_knowledge_mapping(
                                                    tool_knowledge_id_list,
                                                    knowledge_id_list,
                                                    self.data.get("tool_id")))
                return self.one()
            if instance.get("work_flow_template"):
                template_instance = instance.get('work_flow_template')
                download_url = template_instance.get('downloadUrl')
                # 查找匹配的版本名称
                res = requests.get(download_url, timeout=5)
                tool = QuerySet(Tool).filter(id=self.data.get("tool_id")).first()
                ToolSerializer.Import(data={
                    'user_id': self.data.get('user_id'),
                    'workspace_id': workflow_id,
                    'folder_id': tool.folder_id,
                    'file': bytes_to_uploaded_file(res.content, 'file.tool')
                }).update_template_workflow(str(self.data.get('tool_id')))

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


class StoreToolWorkflow(serializers.Serializer):
    user_id = serializers.UUIDField(required=True, label=_("User ID"))
    name = serializers.CharField(required=False, label=_("tool name"), allow_null=True, allow_blank=True)

    def get_appstore_templates(self):
        self.is_valid(raise_exception=True)
        # 下载zip文件
        try:
            res = requests.get('https://apps-assets.fit2cloud.com/stable/maxkb.json.zip', timeout=5)
            res.raise_for_status()
            # 创建临时文件保存zip
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
                temp_zip.write(res.content)
                temp_zip_path = temp_zip.name

            try:
                # 解压zip文件
                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    # 获取zip中的第一个文件（假设只有一个json文件）
                    json_filename = zip_ref.namelist()[0]
                    json_content = zip_ref.read(json_filename)

                # 将json转换为字典
                tool_store = json.loads(json_content.decode('utf-8'))
                tag_dict = {tag['name']: tag['key'] for tag in tool_store['additionalProperties']['tags']}
                filter_apps = []
                for tool in tool_store['apps']:
                    if self.data.get('name', '') != '':
                        if self.data.get('name').lower() not in tool.get('name', '').lower():
                            continue
                    if not tool['downloadUrl'].endswith('.tool') or not [tag_dict[tag] for tag in
                                                                         tool.get('tags')].__contains__(
                        'workflow_template'):
                        continue
                    versions = tool.get('versions', [])
                    tool['label'] = tag_dict[tool.get('tags')[0]] if tool.get('tags') else ''
                    tool['version'] = next(
                        (version.get('name') for version in versions if
                         version.get('downloadUrl') == tool['downloadUrl']),
                    )
                    filter_apps.append(tool)

                tool_store['apps'] = filter_apps
                return tool_store
            finally:
                # 清理临时文件
                os.unlink(temp_zip_path)
        except Exception as e:
            maxkb_logger.error(f"fetch appstore tools error: {e}")
            return {'apps': [], 'additionalProperties': {'tags': []}}


def update_resource_mapping_by_tool(tool_id: str, other_resource_mapping=None):
    from application.flow.tools import get_instance_resource, save_workflow_mapping
    from system_manage.models.resource_mapping import ResourceType
    if other_resource_mapping is None:
        other_resource_mapping = []
    tool = QuerySet(ToolWorkflow).filter(tool_id=tool_id).first()
    instance_mapping = get_instance_resource(tool, ResourceType.TOOL, str(tool_id),
                                             {})
    save_workflow_mapping(tool.work_flow, ResourceType.TOOL, str(tool_id),
                          instance_mapping + other_resource_mapping)

    return
