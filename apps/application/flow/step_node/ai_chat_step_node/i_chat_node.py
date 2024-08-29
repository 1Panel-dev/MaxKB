# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： i_chat_node.py
    @date：2024/6/4 13:58
    @desc:
"""
from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.util.field_message import ErrMessage


class ChatNodeSerializer(serializers.Serializer):
    model_id = serializers.CharField(required=True, error_messages=ErrMessage.char("模型id"))
    system = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                   error_messages=ErrMessage.char("角色设定"))
    prompt = serializers.CharField(required=True, error_messages=ErrMessage.char("提示词"))
    # 多轮对话数量
    dialogue_number = serializers.IntegerField(required=True, error_messages=ErrMessage.integer("多轮对话数量"))

    is_result = serializers.BooleanField(required=False, error_messages=ErrMessage.boolean('是否返回内容'))

    model_params_setting = serializers.DictField(required=False, error_messages=ErrMessage.integer("模型参数相关设置"))


class IChatNode(INode):
    type = 'ai-chat-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return ChatNodeSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, model_id, system, prompt, dialogue_number, history_chat_record, stream, chat_id,
                chat_record_id,
                model_params_setting=None,
                **kwargs) -> NodeResult:
        pass
