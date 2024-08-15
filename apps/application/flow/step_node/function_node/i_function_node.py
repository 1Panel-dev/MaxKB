# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： i_function_lib_node.py
    @date：2024/8/8 16:21
    @desc:
"""
import re
from typing import Type

from django.core import validators
from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.exception.app_exception import AppApiException
from common.field.common import ObjectField
from common.util.field_message import ErrMessage


class InputField(serializers.Serializer):
    name = serializers.CharField(required=True, error_messages=ErrMessage.char('变量名'))
    is_required = serializers.BooleanField(required=True, error_messages=ErrMessage.boolean("是否必填"))
    type = serializers.CharField(required=True, error_messages=ErrMessage.char("类型"), validators=[
        validators.RegexValidator(regex=re.compile("^string|int|dict|array|float$"),
                                  message="字段只支持string|int|dict|array|float", code=500)
    ])
    source = serializers.CharField(required=True, error_messages=ErrMessage.char("来源"), validators=[
        validators.RegexValidator(regex=re.compile("^custom|reference$"),
                                  message="字段只支持custom|reference", code=500)
    ])
    value = ObjectField(required=True, error_messages=ErrMessage.char("变量值"), model_type_list=[str, list])

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        is_required = self.data.get('is_required')
        if is_required and self.data.get('value') is None:
            raise AppApiException(500, f'{self.data.get("name")}必填')


class FunctionNodeParamsSerializer(serializers.Serializer):
    input_field_list = InputField(required=True, many=True)
    code = serializers.CharField(required=True, error_messages=ErrMessage.char("函数"))
    is_result = serializers.BooleanField(required=False, error_messages=ErrMessage.boolean('是否返回内容'))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)


class IFunctionNode(INode):
    type = 'function-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return FunctionNodeParamsSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, input_field_list, code, **kwargs) -> NodeResult:
        pass
