# coding=utf-8

from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from django.utils.translation import gettext_lazy as _


class SpeechToTextNodeSerializer(serializers.Serializer):
    stt_model_id = serializers.CharField(required=True, label=_("Model id"))

    is_result = serializers.BooleanField(required=False,
                                         label=_('Whether to return content'))

    audio_list = serializers.ListField(required=True,
                                       label=_("The audio file cannot be empty"))
    model_params_setting = serializers.DictField(required=False,
                                                 label=_("Model parameter settings"))


class ISpeechToTextNode(INode):
    type = 'speech-to-text-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return SpeechToTextNodeSerializer

    def _run(self):
        res = self.workflow_manage.get_reference_field(self.node_params_serializer.data.get('audio_list')[0],
                                                       self.node_params_serializer.data.get('audio_list')[1:])
        for audio in res:
            if 'file_id' not in audio:
                raise ValueError(
                    _("Parameter value error: The uploaded audio lacks file_id, and the audio upload fails"))

        return self.execute(audio=res, **self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, stt_model_id, chat_id,
                audio, model_params_setting=None,
                **kwargs) -> NodeResult:
        pass
