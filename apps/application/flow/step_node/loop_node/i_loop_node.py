# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： i_loop_node.py
    @date：2025/3/11 18:19
    @desc:
"""
from typing import Type

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.exception.app_exception import AppApiException


class ILoopNodeSerializer(serializers.Serializer):
    loop_type = serializers.CharField(required=True, label=_("loop_type"))
    array = serializers.ListField(required=False, allow_null=True,
                                  label=_("array"))
    number = serializers.IntegerField(required=False, allow_null=True,
                                      label=_("number"))
    loop_body = serializers.DictField(required=True, label="循环体")

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        loop_type = self.data.get('loop_type')
        if loop_type == 'ARRAY':
            array = self.data.get('array')
            if array is None or len(array) == 0:
                message = _('{field}, this field is required.', field='array')
                raise AppApiException(500, message)
        elif loop_type == 'NUMBER':
            number = self.data.get('number')
            if number is None:
                message = _('{field}, this field is required.', field='number')
                raise AppApiException(500, message)


class ILoopNode(INode):
    type = 'loop-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return ILoopNodeSerializer

    def _run(self):
        array = self.node_params_serializer.data.get('array')
        if self.node_params_serializer.data.get('loop_type') == 'ARRAY':
            array = self.workflow_manage.get_reference_field(
                array[0],
                array[1:])
        return self.execute(**{**self.node_params_serializer.data, "array": array}, **self.flow_params_serializer.data)

    def execute(self, loop_type, array, number, loop_body, stream, **kwargs) -> NodeResult:
        pass
