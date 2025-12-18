# coding=utf-8
import asyncio
import json
from typing import Dict

import uuid_utils.compat as uuid
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.common import Workflow, WorkflowMode
from application.flow.i_step_node import KnowledgeWorkflowPostHandler
from application.flow.knowledge_workflow_manage import KnowledgeWorkflowManage
from application.flow.step_node import get_node
from application.serializers.application import get_mcp_tools
from common.constants.cache_version import Cache_Version
from common.db.search import page_search
from common.exception.app_exception import AppApiException
from common.utils.rsa_util import rsa_long_decrypt
from common.utils.tool_code import ToolExecutor
from knowledge.models import KnowledgeScope, Knowledge, KnowledgeType, KnowledgeWorkflow, KnowledgeWorkflowVersion
from knowledge.models.knowledge_action import KnowledgeAction, State
from knowledge.serializers.knowledge import KnowledgeModelSerializer
from django.core.cache import cache
from system_manage.models import AuthTargetType
from system_manage.serializers.user_resource_permission import UserResourcePermissionSerializer
from tools.models import Tool
from users.models import User

tool_executor = ToolExecutor()


class KnowledgeWorkflowModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeWorkflow
        fields = '__all__'


class KnowledgeWorkflowActionRequestSerializer(serializers.Serializer):
    data_source = serializers.DictField(required=True, label=_('datasource data'))
    knowledge_base = serializers.DictField(required=True, label=_('knowledge base data'))


class KnowledgeWorkflowActionListQuerySerializer(serializers.Serializer):
    user_name = serializers.CharField(required=False, label=_('Name'), allow_blank=True, allow_null=True)
    state = serializers.CharField(required=False, label=_("State"), allow_blank=True, allow_null=True)


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
            KnowledgeWorkflowPostHandler(None, knowledge_action_id))
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
            QuerySet(KnowledgeAction).filter(id=knowledge_action_id).update(state=State.REVOKE)
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

            return {**KnowledgeModelSerializer(knowledge).data, 'document_list': []}

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
