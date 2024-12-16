# coding=utf-8

from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.util.field_message import ErrMessage


class ImageGenerateNodeSerializer(serializers.Serializer):
    model_id = serializers.CharField(required=True, error_messages=ErrMessage.char("模型id"))

    prompt = serializers.CharField(required=True, error_messages=ErrMessage.char("提示词(正向)"))

    negative_prompt = serializers.CharField(required=False, error_messages=ErrMessage.char("提示词(负向)"), allow_null=True, allow_blank=True,)
    # 多轮对话数量
    dialogue_number = serializers.IntegerField(required=False, default=0, error_messages=ErrMessage.integer("多轮对话数量"))

    dialogue_type = serializers.CharField(required=False, default='NODE', error_messages=ErrMessage.char("对话存储类型"))

    is_result = serializers.BooleanField(required=False, error_messages=ErrMessage.boolean('是否返回内容'))

    model_params_setting = serializers.JSONField(required=False, default=dict, error_messages=ErrMessage.json("模型参数设置"))


class IImageGenerateNode(INode):
    type = 'image-generate-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return ImageGenerateNodeSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, model_id, prompt, negative_prompt, dialogue_number, dialogue_type, history_chat_record, chat_id,
                model_params_setting,
                chat_record_id,
                **kwargs) -> NodeResult:
        pass
