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

from application.flow.i_step_node import INode
from common.util.field_message import ErrMessage


class ConditionSerializer(serializers.Serializer):
    compare = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Comparator")))
    value = serializers.CharField(required=True, error_messages=ErrMessage.char(_("value")))
    field = serializers.ListField(required=True, error_messages=ErrMessage.char(_("Fields")))


class ConditionBranchSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Branch id")))
    type = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Branch Type")))
    condition = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Condition or|and")))
    conditions = ConditionSerializer(many=True)


class ConditionNodeParamsSerializer(serializers.Serializer):
    branch = ConditionBranchSerializer(many=True)


class IConditionNode(INode):
    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return ConditionNodeParamsSerializer

    type = 'condition-node'
