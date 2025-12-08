# coding=utf-8

from typing import Type

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult




class VariableListSerializer(serializers.Serializer):
    v_id = serializers.CharField(required=True, label=_("Variable id"))
    variable = serializers.ListField(required=True, label=_("Variable"))


class VariableGroupSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, label=_("Group id"))
    field = serializers.CharField(required=True, label=_("group_name"))
    label = serializers.CharField(required=True)
    variable_list = VariableListSerializer(many=True)


class VariableAggregationNodeSerializer(serializers.Serializer):
    strategy = serializers.CharField(required=True, label=_("Strategy"))
    group_list = VariableGroupSerializer(many=True)


class IVariableAggregation(INode):
    type = 'variable-aggregation-node'


    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return VariableAggregationNodeSerializer

    def _run(self):
        return  self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self,strategy,group_list,**kwargs) -> NodeResult:
        pass


