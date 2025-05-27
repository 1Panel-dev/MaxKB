# coding=utf-8

from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.util.field_message import ErrMessage
from django.utils.translation import gettext_lazy as _


class TextToSpeechNodeSerializer(serializers.Serializer):
    tts_model_id = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Model id")))

    is_result = serializers.BooleanField(required=False, error_messages=ErrMessage.boolean(_('Whether to return content')))

    content_list = serializers.ListField(required=True, error_messages=ErrMessage.list(_("Text content")))
    model_params_setting = serializers.DictField(required=False,
                                                 error_messages=ErrMessage.integer(_("Model parameter settings")))


class ITextToSpeechNode(INode):
    type = 'text-to-speech-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return TextToSpeechNodeSerializer

    def _run(self):
        content = self.workflow_manage.get_reference_field(self.node_params_serializer.data.get('content_list')[0],
                                                           self.node_params_serializer.data.get('content_list')[1:])
        return self.execute(content=content, **self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, tts_model_id, chat_id,
                content, model_params_setting=None,
                **kwargs) -> NodeResult:
        pass
