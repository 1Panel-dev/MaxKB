# coding=utf-8

from typing import Type

from rest_framework import serializers

from application.flow.common import WorkflowMode
from application.flow.i_step_node import INode, NodeResult

from django.utils.translation import gettext_lazy as _


class TextToSpeechNodeSerializer(serializers.Serializer):
    tts_model_id = serializers.CharField(required=True, label=_("Model id"))

    is_result = serializers.BooleanField(required=False,
                                         label=_('Whether to return content'))

    content_list = serializers.ListField(required=True, label=_("Text content"))
    model_params_setting = serializers.DictField(required=False,
                                                 label=_("Model parameter settings"))


class ITextToSpeechNode(INode):
    type = 'text-to-speech-node'
    support = [WorkflowMode.APPLICATION, WorkflowMode.APPLICATION_LOOP, WorkflowMode.KNOWLEDGE,
               WorkflowMode.KNOWLEDGE_LOOP]

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return TextToSpeechNodeSerializer

    def _run(self):
        content = self.workflow_manage.get_reference_field(self.node_params_serializer.data.get('content_list')[0],
                                                           self.node_params_serializer.data.get('content_list')[1:])
        return self.execute(content=content, **self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, tts_model_id,
                content, model_params_setting=None,
                **kwargs) -> NodeResult:
        pass
