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
from django.utils.translation import gettext_lazy as _
from rest_framework.utils.formatting import lazy_format


class InputField(serializers.Serializer):
    name = serializers.CharField(required=True, error_messages=ErrMessage.char(_('Variable Name')))
    is_required = serializers.BooleanField(required=True, error_messages=ErrMessage.boolean(_("Is this field required")))
    type = serializers.CharField(required=True, error_messages=ErrMessage.char(_("type")), validators=[
        validators.RegexValidator(regex=re.compile("^string|int|dict|array|float$"),
                                  message=_("The field only supports string|int|dict|array|float"), code=500)
    ])
    source = serializers.CharField(required=True, error_messages=ErrMessage.char(_("source")), validators=[
        validators.RegexValidator(regex=re.compile("^custom|reference$"),
                                  message=_("The field only supports custom|reference"), code=500)
    ])
    value = ObjectField(required=True, error_messages=ErrMessage.char(_("Variable Value")), model_type_list=[str, list])

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        is_required = self.data.get('is_required')
        if is_required and self.data.get('value') is None:
            message = lazy_format(_('{field}, this field is required.'), field=self.data.get("name"))
            raise AppApiException(500, message)


class FunctionNodeParamsSerializer(serializers.Serializer):
    input_field_list = InputField(required=True, many=True)
    code = serializers.CharField(required=True, error_messages=ErrMessage.char(_("function")))
    is_result = serializers.BooleanField(required=False, error_messages=ErrMessage.boolean(_('Whether to return content')))

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
