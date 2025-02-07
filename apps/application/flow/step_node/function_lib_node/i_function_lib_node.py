# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： i_function_lib_node.py
    @date：2024/8/8 16:21
    @desc:
"""
from typing import Type

from django.db.models import QuerySet
from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.field.common import ObjectField
from common.util.field_message import ErrMessage
from function_lib.models.function import FunctionLib
from django.utils.translation import gettext_lazy as _


class InputField(serializers.Serializer):
    name = serializers.CharField(required=True, error_messages=ErrMessage.char(_('Variable Name')))
    value = ObjectField(required=True, error_messages=ErrMessage.char(_("Variable Value")), model_type_list=[str, list])


class FunctionLibNodeParamsSerializer(serializers.Serializer):
    function_lib_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('Library ID')))
    input_field_list = InputField(required=True, many=True)
    is_result = serializers.BooleanField(required=False, error_messages=ErrMessage.boolean(_('Whether to return content')))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        f_lib = QuerySet(FunctionLib).filter(id=self.data.get('function_lib_id')).first()
        if f_lib is None:
            raise Exception(_('The function has been deleted'))


class IFunctionLibNode(INode):
    type = 'function-lib-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return FunctionLibNodeParamsSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, function_lib_id, input_field_list, **kwargs) -> NodeResult:
        pass
