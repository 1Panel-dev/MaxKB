# coding=utf-8

from typing import Type

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.common import WorkflowMode
from application.flow.i_step_node import INode, NodeResult


class IntentBranchSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, label=_("Branch id"))
    content = serializers.CharField(required=True, label=_("content"))
    isOther = serializers.BooleanField(required=True, label=_("Branch Type"))


class IntentNodeSerializer(serializers.Serializer):
    model_id = serializers.CharField(required=True, label=_("Model id"))
    content_list = serializers.ListField(required=True, label=_("Text content"))
    dialogue_number = serializers.IntegerField(required=True, label=
    _("Number of multi-round conversations"))
    model_params_setting = serializers.DictField(required=False,
                                                 label=_("Model parameter settings"))
    branch = IntentBranchSerializer(many=True)


class IIntentNode(INode):
    type = 'intent-node'
    support = [WorkflowMode.APPLICATION, WorkflowMode.APPLICATION_LOOP, WorkflowMode.KNOWLEDGE,
               WorkflowMode.KNOWLEDGE_LOOP]

    def save_context(self, details, workflow_manage):
        pass

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return IntentNodeSerializer

    def _run(self):
        question = self.workflow_manage.get_reference_field(
            self.node_params_serializer.data.get('content_list')[0],
            self.node_params_serializer.data.get('content_list')[1:],
        )
        if [WorkflowMode.KNOWLEDGE, WorkflowMode.KNOWLEDGE_LOOP].__contains__(
                self.workflow_manage.flow.workflow_mode):
            return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data,
                                **{'history_chat_record': [], 'stream': True, 'chat_id': None, 'chat_record_id': None,
                                   'user_input': str(question)})
        else:
            return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data,
                                user_input=str(question))

    def execute(self, model_id, dialogue_number, history_chat_record, user_input, branch,
                model_params_setting=None, **kwargs) -> NodeResult:
        pass
