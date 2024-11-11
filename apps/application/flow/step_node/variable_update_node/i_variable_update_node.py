# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： i_reply_node.py
    @date：2024/6/11 16:25
    @desc:
"""
from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult, chat_cache
from common.exception.app_exception import AppApiException
from common.util.field_message import ErrMessage


class VariableUpdateNodeParamsSerializer(serializers.Serializer):
    value_type = serializers.CharField(required=True, error_messages=ErrMessage.char("更新类型，引用变量值/自定义"))
    fields = serializers.ListField(required=False, error_messages=ErrMessage.list("待变更的变量"))
    content = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                    error_messages=ErrMessage.char("自定义内容"))
    target_value = serializers.ListField(required=False, error_messages=ErrMessage.char("引用的变量值"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        if self.data.get('value_type') == 'referencing':
            if 'fields' not in self.data:
                raise AppApiException(500, "变量字段不能为空")
            if len(self.data.get('fields')) < 2:
                raise AppApiException(500, "变量字段错误")
            if 'target_value' not in self.data:
                raise AppApiException(500, "引用的参数不能为空")
            if len(self.data.get('target_value')) < 2:
                raise AppApiException(500, "引用的参数错误")
        else:
            if 'content' not in self.data or self.data.get('content') is None:
                raise AppApiException(500, "内容不能为空")


class IVariableUpdateNode(INode):
    type = 'variable-update-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return VariableUpdateNodeParamsSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, value_type, stream, fields=None, content=None, target_value=None, **kwargs) -> NodeResult:
        pass
