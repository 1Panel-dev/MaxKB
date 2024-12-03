# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： i_form_node.py
    @date：2024/11/4 14:48
    @desc:
"""
from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.util.field_message import ErrMessage


class FormNodeParamsSerializer(serializers.Serializer):
    form_field_list = serializers.ListField(required=True, error_messages=ErrMessage.list("表单配置"))
    form_content_format = serializers.CharField(required=True, error_messages=ErrMessage.char('表单输出内容'))
    form_data = serializers.DictField(required=False, allow_null=True, error_messages=ErrMessage.dict("表单数据"))


class IFormNode(INode):
    type = 'form-node'
    view_type = 'single_view'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return FormNodeParamsSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, form_field_list, form_content_format, form_data, **kwargs) -> NodeResult:
        pass
