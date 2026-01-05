# coding=utf-8
import asyncio
import json
import pickle
from functools import reduce
from typing import Dict, List

import requests
import uuid_utils.compat as uuid
from django.core.cache import cache
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status

from application.flow.common import Workflow, WorkflowMode
from application.flow.i_step_node import KnowledgeWorkflowPostHandler
from application.flow.knowledge_workflow_manage import KnowledgeWorkflowManage
from application.flow.step_node import get_node
from application.flow.tools import save_workflow_mapping
from application.serializers.application import get_mcp_tools
from common.constants.cache_version import Cache_Version
from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.field.common import UploadedFileField
from common.result import result
from common.utils.common import bytes_to_uploaded_file
from common.utils.common import restricted_loads, generate_uuid
from common.utils.logger import maxkb_logger
from common.utils.rsa_util import rsa_long_decrypt
from common.utils.tool_code import ToolExecutor
from knowledge.models import KnowledgeScope, Knowledge, KnowledgeType, KnowledgeWorkflow, KnowledgeWorkflowVersion
from knowledge.models.knowledge_action import KnowledgeAction, State
from knowledge.serializers.common import update_resource_mapping_by_knowledge
from knowledge.serializers.knowledge import KnowledgeModelSerializer
from system_manage.models import AuthTargetType
from system_manage.models.resource_mapping import ResourceType
from system_manage.serializers.user_resource_permission import UserResourcePermissionSerializer
from tools.models import Tool, ToolScope
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


class KnowledgeWorkflowModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeWorkflow
        fields = '__all__'


class KnowledgeWorkflowActionRequestSerializer(serializers.Serializer):
    data_source = serializers.DictField(required=True, label=_('datasource data'))
    knowledge_base = serializers.DictField(required=True, label=_('knowledge base data'))


class KnowledgeWorkflowImportRequest(serializers.Serializer):
    file = UploadedFileField(required=True, label=_("file"))


class KnowledgeWorkflowActionListQuerySerializer(serializers.Serializer):
    user_name = serializers.CharField(required=False, label=_('Name'), allow_blank=True, allow_null=True)
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
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))
    knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))

    def get_query_set(self, instance: Dict):
        query_set = QuerySet(KnowledgeAction).filter(knowledge_id=self.data.get('knowledge_id')).values('id',
                                                                                                        'knowledge_id',
                                                                                                        "state", 'meta',
                                                                                                        'run_time',
                                                                                                        "create_time")
        if instance.get("user_name"):
            query_set = query_set.filter(meta__user_name__icontains=instance.get('user_name'))
        if instance.get('state'):
            query_set = query_set.filter(state=instance.get('state'))
        return query_set.order_by('-create_time')

    def list(self, instance: Dict, is_valid=True):
        if is_valid:
            self.is_valid(raise_exception=True)
            KnowledgeWorkflowActionListQuerySerializer(data=instance).is_valid(raise_exception=True)
        return [{'id': a.get("id"), 'knowledge_id': a.get("knowledge_id"), 'state': a.get("state"),
                 'meta': a.get("meta"), 'run_time': a.get("run_time"), 'create_time': a.get("create_time")} for a in
                self.get_query_set(instance)]

    def page(self, current_page, page_size, instance: Dict, is_valid=True):
        if is_valid:
            self.is_valid(raise_exception=True)
            KnowledgeWorkflowActionListQuerySerializer(data=instance).is_valid(raise_exception=True)
        return page_search(current_page, page_size, self.get_query_set(instance),
                           lambda a: {'id': a.get("id"), 'knowledge_id': a.get("knowledge_id"), 'state': a.get("state"),
                                      'meta': a.get("meta"), 'run_time': a.get("run_time"),
                                      'create_time': a.get("create_time")})

    def action(self, instance: Dict, user, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        knowledge_workflow = QuerySet(KnowledgeWorkflow).filter(knowledge_id=self.data.get("knowledge_id")).first()
        knowledge_action_id = uuid.uuid7()
        meta = {'user_id': str(user.id),
                'user_name': user.username}
        KnowledgeAction(id=knowledge_action_id,
                        knowledge_id=self.data.get("knowledge_id"),
                        state=State.STARTED,
                        meta=meta).save()
        work_flow_manage = KnowledgeWorkflowManage(
            Workflow.new_instance(knowledge_workflow.work_flow, WorkflowMode.KNOWLEDGE),
            {'knowledge_id': self.data.get("knowledge_id"), 'knowledge_action_id': knowledge_action_id, 'stream': True,
             'workspace_id': self.data.get("workspace_id"),
             **instance},
            KnowledgeWorkflowPostHandler(None, knowledge_action_id),
            is_the_task_interrupted=lambda: cache.get(
                Cache_Version.KNOWLEDGE_WORKFLOW_INTERRUPTED.get_key(action_id=knowledge_action_id),
                version=Cache_Version.KNOWLEDGE_WORKFLOW_INTERRUPTED.get_version()) or False)
        work_flow_manage.run()
        return {'id': knowledge_action_id, 'knowledge_id': self.data.get("knowledge_id"), 'state': State.STARTED,
                'details': {}, 'meta': meta}

    def upload_document(self, instance: Dict, user, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        knowledge_workflow = QuerySet(KnowledgeWorkflow).filter(knowledge_id=self.data.get("knowledge_id")).first()
        if not knowledge_workflow.is_publish:
            raise AppApiException(500, _("The knowledge base workflow has not been published"))
        knowledge_workflow_version = QuerySet(KnowledgeWorkflowVersion).filter(
            knowledge_id=self.data.get("knowledge_id")).order_by(
            '-create_time')[0:1].first()
        knowledge_action_id = uuid.uuid7()
        meta = {'user_id': str(user.id),
                'user_name': user.username}
        KnowledgeAction(id=knowledge_action_id, knowledge_id=self.data.get("knowledge_id"), state=State.STARTED,
                        meta=meta).save()
        work_flow_manage = KnowledgeWorkflowManage(
            Workflow.new_instance(knowledge_workflow_version.work_flow, WorkflowMode.KNOWLEDGE),
            {'knowledge_id': self.data.get("knowledge_id"), 'knowledge_action_id': knowledge_action_id, 'stream': True,
             'workspace_id': self.data.get("workspace_id"),
             **instance},
            KnowledgeWorkflowPostHandler(None, knowledge_action_id),
            is_the_task_interrupted=lambda: cache.get(
                Cache_Version.KNOWLEDGE_WORKFLOW_INTERRUPTED.get_key(action_id=knowledge_action_id),
                version=Cache_Version.KNOWLEDGE_WORKFLOW_INTERRUPTED.get_version()) or False
        )
        work_flow_manage.run()
        return {'id': knowledge_action_id, 'knowledge_id': self.data.get("knowledge_id"), 'state': State.STARTED,
                'details': {}, 'meta': meta}

    class Operate(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))
        id = serializers.UUIDField(required=True, label=_('knowledge action id'))

        def one(self, is_valid=True):
            if is_valid:
                self.is_valid(raise_exception=True)
            knowledge_action_id = self.data.get("id")
            knowledge_action = QuerySet(KnowledgeAction).filter(id=knowledge_action_id).first()
            return {'id': knowledge_action_id, 'knowledge_id': knowledge_action.knowledge_id,
                    'state': knowledge_action.state,
                    'details': knowledge_action.details,
                    'meta': knowledge_action.meta}

        def cancel(self, is_valid=True):
            if is_valid:
                self.is_valid(raise_exception=True)
            knowledge_action_id = self.data.get("id")
            cache.set(Cache_Version.KNOWLEDGE_WORKFLOW_INTERRUPTED.get_key(action_id=knowledge_action_id), True,
                      version=Cache_Version.KNOWLEDGE_WORKFLOW_INTERRUPTED.get_version())
            QuerySet(KnowledgeAction).filter(id=knowledge_action_id, state__in=[State.STARTED, State.PENDING]).update(
                state=State.REVOKE)
            return True


class KnowledgeWorkflowSerializer(serializers.Serializer):
    class Datasource(serializers.Serializer):
        type = serializers.CharField(required=True, label=_('type'))
        id = serializers.CharField(required=True, label=_('type'))
        params = serializers.DictField(required=True, label="")
        function_name = serializers.CharField(required=True, label=_('function_name'))

        def action(self):
            self.is_valid(raise_exception=True)
            if self.data.get('type') == 'local':
                node = get_node(self.data.get('id'), WorkflowMode.KNOWLEDGE)
                return node.__getattribute__(node, self.data.get("function_name"))(**self.data.get("params"))
            elif self.data.get('type') == 'tool':
                tool = QuerySet(Tool).filter(id=self.data.get("id")).first()
                init_params = json.loads(rsa_long_decrypt(tool.init_params))
                return tool_executor.exec_code(tool.code, {**init_params, **self.data.get('params')},
                                               self.data.get('function_name'))

    class Create(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        scope = serializers.ChoiceField(
            required=False, label=_('scope'), default=KnowledgeScope.WORKSPACE, choices=KnowledgeScope.choices
        )

        @transaction.atomic
        def save_workflow(self, instance: Dict):
            self.is_valid(raise_exception=True)

            folder_id = instance.get('folder_id', self.data.get('workspace_id'))

            knowledge_id = uuid.uuid7()
            knowledge = Knowledge(
                id=knowledge_id,
                name=instance.get('name'),
                desc=instance.get('desc'),
                user_id=self.data.get('user_id'),
                type=instance.get('type', KnowledgeType.WORKFLOW),
                scope=self.data.get('scope', KnowledgeScope.WORKSPACE),
                folder_id=folder_id,
                workspace_id=self.data.get('workspace_id'),
                embedding_model_id=instance.get('embedding_model_id'),
                meta={},
            )
            knowledge.save()
            # 自动资源给授权当前用户
            UserResourcePermissionSerializer(data={
                'workspace_id': self.data.get('workspace_id'),
                'user_id': self.data.get('user_id'),
                'auth_target_type': AuthTargetType.KNOWLEDGE.value
            }).auth_resource(str(knowledge_id))

            knowledge_workflow = KnowledgeWorkflow(
                id=uuid.uuid7(),
                knowledge_id=knowledge_id,
                workspace_id=self.data.get('workspace_id'),
                work_flow=instance.get('work_flow', {}),
            )

            knowledge_workflow.save()
            save_workflow_mapping(instance.get('work_flow', {}), ResourceType.KNOWLEDGE, str(knowledge_id))

            # 处理 work_flow_template
            if instance.get('work_flow_template') is not None:
                template_instance = instance.get('work_flow_template')
                download_url = template_instance.get('downloadUrl')
                # 查找匹配的版本名称
                res = requests.get(download_url, timeout=5)
                KnowledgeWorkflowSerializer.Import(data={
                    'user_id': self.data.get('user_id'),
                    'workspace_id': self.data.get('workspace_id'),
                    'knowledge_id': str(knowledge_id),
                }).import_({'file': bytes_to_uploaded_file(res.content, 'file.kbwf')}, is_import_tool=True)

                try:
                    requests.get(template_instance.get('downloadCallbackUrl'), timeout=5)
                except Exception as e:
                    maxkb_logger.error(f"callback appstore tool download error: {e}")

            return {**KnowledgeModelSerializer(knowledge).data, 'document_list': []}

    class Import(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        workspace_id = serializers.CharField(required=False, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))

        @transaction.atomic
        def import_(self, instance: dict, is_import_tool, with_valid=True):
            if with_valid:
                self.is_valid()
                KnowledgeWorkflowImportRequest(data=instance).is_valid(raise_exception=True)
            user_id = self.data.get('user_id')
            workspace_id = self.data.get('workspace_id')
            knowledge_id = self.data.get('knowledge_id')
            kbwf_instance_bytes = instance.get('file').read()
            try:
                kbwf_instance = restricted_loads(kbwf_instance_bytes)
            except Exception as e:
                raise AppApiException(1001, _("Unsupported file format"))
            knowledge_workflow = kbwf_instance.knowledge_workflow
            tool_list = kbwf_instance.get_tool_list()
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

            work_flow = self.to_knowledge_workflow(
                knowledge_workflow,
                update_tool_map,
            )
            tool_model_list = [self.to_tool(tool, workspace_id, user_id) for tool in tool_list]
            KnowledgeWorkflow.objects.filter(workspace_id=workspace_id, knowledge_id=knowledge_id).update_or_create(
                knowledge_id=knowledge_id,
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
                return True
            update_resource_mapping_by_knowledge(knowledge_id)

        @staticmethod
        def to_knowledge_workflow(knowledge_workflow, update_tool_map):
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
                        scope=ToolScope.SHARED if workspace_id == 'None' else ToolScope.WORKSPACE,
                        folder_id='default' if workspace_id == 'None' else workspace_id,
                        workspace_id=workspace_id)

    class Export(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        workspace_id = serializers.CharField(required=False, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))

        def export(self, with_valid=True):
            try:
                if with_valid:
                    self.is_valid()
                knowledge_id = self.data.get('knowledge_id')
                knowledge_workflow = QuerySet(KnowledgeWorkflow).filter(knowledge_id=knowledge_id).first()
                knowledge = QuerySet(Knowledge).filter(id=knowledge_id).first()
                from application.flow.tools import get_tool_id_list
                tool_id_list = get_tool_id_list(knowledge_workflow.work_flow)
                tool_list = []
                if len(tool_id_list) > 0:
                    tool_list = QuerySet(Tool).filter(id__in=tool_id_list).exclude(scope=ToolScope.SHARED)
                knowledge_workflow_dict = KnowledgeWorkflowModelSerializer(knowledge_workflow).data

                kbwf_instance = KBWFInstance(
                    knowledge_workflow_dict,
                    [],
                    'v2',
                    [ToolExportModelSerializer(tool).data for tool in tool_list]
                )
                knowledge_workflow_pickle = pickle.dumps(kbwf_instance)
                response = HttpResponse(content_type='text/plain', content=knowledge_workflow_pickle)
                response['Content-Disposition'] = f'attachment; filename="{knowledge.name}.kbwf"'
                return response
            except Exception as e:
                return result.error(str(e), response_status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    class Operate(serializers.Serializer):
        user_id = serializers.UUIDField(required=True, label=_('user id'))
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))

        def publish(self, with_valid=True):
            if with_valid:
                self.is_valid()
            user_id = self.data.get('user_id')
            workspace_id = self.data.get("workspace_id")
            user = QuerySet(User).filter(id=user_id).first()
            knowledge_workflow = QuerySet(KnowledgeWorkflow).filter(knowledge_id=self.data.get("knowledge_id"),
                                                                    workspace_id=workspace_id).first()
            work_flow_version = KnowledgeWorkflowVersion(work_flow=knowledge_workflow.work_flow,
                                                         knowledge_id=self.data.get("knowledge_id"),
                                                         name=timezone.localtime(timezone.now()).strftime(
                                                             '%Y-%m-%d %H:%M:%S'),
                                                         publish_user_id=user_id,
                                                         publish_user_name=user.username,
                                                         workspace_id=workspace_id)
            work_flow_version.save()
            QuerySet(KnowledgeWorkflow).filter(
                knowledge_id=self.data.get("knowledge_id")
            ).update(is_publish=True, publish_time=timezone.now())
            return True

        def edit(self, instance: Dict):
            self.is_valid(raise_exception=True)
            if instance.get("work_flow"):
                QuerySet(KnowledgeWorkflow).update_or_create(knowledge_id=self.data.get("knowledge_id"),
                                                             create_defaults={'id': uuid.uuid7(),
                                                                              'knowledge_id': self.data.get(
                                                                                  "knowledge_id"),
                                                                              "workspace_id": self.data.get(
                                                                                  'workspace_id'),
                                                                              'work_flow': instance.get('work_flow',
                                                                                                        {}), },
                                                             defaults={
                                                                 'work_flow': instance.get('work_flow')
                                                             })
                update_resource_mapping_by_knowledge(self.data.get("knowledge_id"))
                return self.one()
            if instance.get("work_flow_template"):
                template_instance = instance.get('work_flow_template')
                download_url = template_instance.get('downloadUrl')
                # 查找匹配的版本名称
                res = requests.get(download_url, timeout=5)
                KnowledgeWorkflowSerializer.Import(data={
                    'user_id': self.data.get('user_id'),
                    'workspace_id': self.data.get('workspace_id'),
                    'knowledge_id': str(self.data.get('knowledge_id')),
                }).import_({'file': bytes_to_uploaded_file(res.content, 'file.kbwf')}, is_import_tool=False)

                try:
                    requests.get(template_instance.get('downloadCallbackUrl'), timeout=5)
                except Exception as e:
                    maxkb_logger.error(f"callback appstore tool download error: {e}")

                return self.one()

        def one(self):
            self.is_valid(raise_exception=True)
            workflow = QuerySet(KnowledgeWorkflow).filter(knowledge_id=self.data.get('knowledge_id')).first()
            return {**KnowledgeWorkflowModelSerializer(workflow).data}


class McpServersSerializer(serializers.Serializer):
    mcp_servers = serializers.JSONField(required=True)


class KnowledgeWorkflowMcpSerializer(serializers.Serializer):
    knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))
    user_id = serializers.UUIDField(required=True, label=_("User ID"))
    workspace_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("Workspace ID"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        workspace_id = self.data.get('workspace_id')
        query_set = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id'))
        if workspace_id:
            query_set = query_set.filter(workspace_id=workspace_id)
        if not query_set.exists():
            raise AppApiException(500, _('Knowledge id does not exist'))

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
