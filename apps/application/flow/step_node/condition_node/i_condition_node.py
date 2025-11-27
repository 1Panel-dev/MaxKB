# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： i_condition_node.py
    @date：2024/6/7 9:54
    @desc:
"""
from typing import Type

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.common import WorkflowMode
from application.flow.i_step_node import INode


class ConditionSerializer(serializers.Serializer):
    compare = serializers.CharField(required=True, label=_("Comparator"))
    value = serializers.CharField(required=True, label=_("value"))
    field = serializers.ListField(required=True, label=_("Fields"))


class ConditionBranchSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, label=_("Branch id"))
    type = serializers.CharField(required=True, label=_("Branch Type"))
    condition = serializers.CharField(required=True, label=_("Condition or|and"))
    conditions = ConditionSerializer(many=True)


class ConditionNodeParamsSerializer(serializers.Serializer):
    branch = ConditionBranchSerializer(many=True)


class IConditionNode(INode):
    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return ConditionNodeParamsSerializer

    type = 'condition-node'

    support = [WorkflowMode.APPLICATION, WorkflowMode.APPLICATION_LOOP, WorkflowMode.KNOWLEDGE, WorkflowMode.KNOWLEDGE_LOOP]
