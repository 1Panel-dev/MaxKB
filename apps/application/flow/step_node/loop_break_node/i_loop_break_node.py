# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： i_loop_break_node.py
    @date：2025/9/15 12:14
    @desc:
"""
from typing import Type

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.i_step_node import INode
from application.flow.i_step_node import NodeResult


class ConditionSerializer(serializers.Serializer):
    compare = serializers.CharField(required=True, label=_("Comparator"))
    value = serializers.CharField(required=True, label=_("value"))
    field = serializers.ListField(required=True, label=_("Fields"))


class LoopBreakNodeSerializer(serializers.Serializer):
    condition = serializers.CharField(required=True, label=_("Condition or|and"))
    condition_list = ConditionSerializer(many=True)


class ILoopBreakNode(INode):
    type = 'loop-break-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return LoopBreakNodeSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data)

    def execute(self, condition, condition_list, **kwargs) -> NodeResult:
        pass
