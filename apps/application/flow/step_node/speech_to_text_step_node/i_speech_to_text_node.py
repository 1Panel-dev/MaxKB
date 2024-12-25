# coding=utf-8

from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.util.field_message import ErrMessage


class SpeechToTextNodeSerializer(serializers.Serializer):
    stt_model_id = serializers.CharField(required=True, error_messages=ErrMessage.char("模型id"))

    is_result = serializers.BooleanField(required=False, error_messages=ErrMessage.boolean('是否返回内容'))

    audio_list = serializers.ListField(required=True, error_messages=ErrMessage.list("音频文件不能为空", ))


class ISpeechToTextNode(INode):
    type = 'speech-to-text-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return SpeechToTextNodeSerializer

    def _run(self):
        res = self.workflow_manage.get_reference_field(self.node_params_serializer.data.get('audio_list')[0],
                                                       self.node_params_serializer.data.get('audio_list')[1:])
        for audio in res:
            if 'file_id' not in audio:
                raise ValueError("参数值错误: 上传的音频中缺少file_id，音频上传失败")

        return self.execute(audio=res, **self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, stt_model_id, chat_id,
                audio,
                **kwargs) -> NodeResult:
        pass
