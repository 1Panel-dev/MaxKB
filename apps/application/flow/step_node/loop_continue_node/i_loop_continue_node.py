# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： i_loop_continue_node.py
    @date：2025/9/15 12:13
    @desc:
"""
from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from django.utils.translation import gettext_lazy as _


class ConditionSerializer(serializers.Serializer):
    compare = serializers.CharField(required=True, label=_("Comparator"))
    value = serializers.CharField(required=True, label=_("value"))
    field = serializers.ListField(required=True, label=_("Fields"))


class LoopContinueNodeSerializer(serializers.Serializer):
    condition = serializers.CharField(required=True, label=_("Condition or|and"))
    condition_list = ConditionSerializer(many=True)


class ILoopContinueNode(INode):
    type = 'loop-continue-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return LoopContinueNodeSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data)

    def execute(self, condition, condition_list, **kwargs) -> NodeResult:
        pass
