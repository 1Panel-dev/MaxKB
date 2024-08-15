# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： i_function_lib_node.py
    @date：2024/8/8 16:21
    @desc:
"""
from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.field.common import ObjectField
from common.util.field_message import ErrMessage


class InputField(serializers.Serializer):
    name = serializers.CharField(required=True, error_messages=ErrMessage.char('变量名'))
    value = ObjectField(required=True, error_messages=ErrMessage.char("变量值"), model_type_list=[str, list])


class FunctionLibNodeParamsSerializer(serializers.Serializer):
    function_lib_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid('函数库id'))
    input_field_list = InputField(required=True, many=True)
    is_result = serializers.BooleanField(required=False, error_messages=ErrMessage.boolean('是否返回内容'))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)


class IFunctionLibNode(INode):
    type = 'function-lib-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return FunctionLibNodeParamsSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, function_lib_id, input_field_list, **kwargs) -> NodeResult:
        pass
