# coding=utf-8
import json
from typing import Dict

import uuid_utils.compat as uuid
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.common import Workflow, WorkflowMode
from application.flow.i_step_node import KnowledgeWorkflowPostHandler
from application.flow.knowledge_workflow_manage import KnowledgeWorkflowManage
from application.flow.step_node import get_node
from common.exception.app_exception import AppApiException
from common.utils.rsa_util import rsa_long_decrypt
from common.utils.tool_code import ToolExecutor
from knowledge.models import KnowledgeScope, Knowledge, KnowledgeType, KnowledgeWorkflow
from knowledge.models.knowledge_action import KnowledgeAction, State
from knowledge.serializers.knowledge import KnowledgeModelSerializer
from maxkb.const import CONFIG
from system_manage.models import AuthTargetType
from system_manage.serializers.user_resource_permission import UserResourcePermissionSerializer
from tools.models import Tool

tool_executor = ToolExecutor(CONFIG.get('SANDBOX'))


class KnowledgeWorkflowModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeWorkflow
        fields = '__all__'


class KnowledgeWorkflowActionSerializer(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_('workspace id'))
    knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))

    def action(self, instance: Dict, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        knowledge_workflow = QuerySet(KnowledgeWorkflow).filter(knowledge_id=self.data.get("knowledge_id")).first()
        knowledge_action_id = uuid.uuid7()
        KnowledgeAction(id=knowledge_action_id, knowledge_id=self.data.get("knowledge_id"), state=State.STARTED).save()
        work_flow_manage = KnowledgeWorkflowManage(
            Workflow.new_instance(knowledge_workflow.work_flow, WorkflowMode.KNOWLEDGE),
            {'knowledge_id': self.data.get("knowledge_id"), 'knowledge_action_id': knowledge_action_id, 'stream': True,
             'workspace_id': self.data.get("workspace_id"),
             **instance},
            KnowledgeWorkflowPostHandler(None, knowledge_action_id))
        work_flow_manage.run()
        return {'id': knowledge_action_id, 'knowledge_id': self.data.get("knowledge_id"), 'state': State.STARTED,
                'details': {}}

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
                    'details': knowledge_action.details}


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
            if QuerySet(Knowledge).filter(
                    workspace_id=self.data.get('workspace_id'), folder_id=folder_id, name=instance.get('name')
            ).exists():
                raise AppApiException(500, _('Knowledge base name duplicate!'))

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

        def edit(self, instance: Dict):
            pass

        def one(self):
            self.is_valid(raise_exception=True)
            workflow = QuerySet(KnowledgeWorkflow).filter(knowledge_id=self.data.get('knowledge_id')).first()
            return {**KnowledgeWorkflowModelSerializer(workflow).data}
