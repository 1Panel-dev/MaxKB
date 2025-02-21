# coding=utf-8

from typing import Type

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.util.field_message import ErrMessage


class VariableAssignNodeParamsSerializer(serializers.Serializer):
    variable_list = serializers.ListField(required=True,
                                          error_messages=ErrMessage.list(_("Reference Field")))


class IVariableAssignNode(INode):
    type = 'variable-assign-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return VariableAssignNodeParamsSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, variable_list, stream, **kwargs) -> NodeResult:
        pass
