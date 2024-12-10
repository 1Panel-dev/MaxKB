# coding=utf-8

from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.util.field_message import ErrMessage


class ImageUnderstandNodeSerializer(serializers.Serializer):
    model_id = serializers.CharField(required=True, error_messages=ErrMessage.char("模型id"))
    system = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                   error_messages=ErrMessage.char("角色设定"))
    prompt = serializers.CharField(required=True, error_messages=ErrMessage.char("提示词"))
    # 多轮对话数量
    dialogue_number = serializers.IntegerField(required=True, error_messages=ErrMessage.integer("多轮对话数量"))

    dialogue_type = serializers.CharField(required=True, error_messages=ErrMessage.char("对话存储类型"))

    is_result = serializers.BooleanField(required=False, error_messages=ErrMessage.boolean('是否返回内容'))

    image_list = serializers.ListField(required=False, error_messages=ErrMessage.list("图片"))

    model_params_setting = serializers.JSONField(required=False, default=dict, error_messages=ErrMessage.json("模型参数设置"))



class IImageUnderstandNode(INode):
    type = 'image-understand-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return ImageUnderstandNodeSerializer

    def _run(self):
        res = self.workflow_manage.get_reference_field(self.node_params_serializer.data.get('image_list')[0],
                                                       self.node_params_serializer.data.get('image_list')[1:])
        return self.execute(image=res, **self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, model_id, system, prompt, dialogue_number, dialogue_type, history_chat_record, stream, chat_id,
                model_params_setting,
                chat_record_id,
                image,
                **kwargs) -> NodeResult:
        pass
