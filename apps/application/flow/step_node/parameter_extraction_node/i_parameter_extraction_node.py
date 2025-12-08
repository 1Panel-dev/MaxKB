# coding=utf-8

from typing import Type

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult


class VariableSplittingNodeParamsSerializer(serializers.Serializer):
    input_variable = serializers.ListField(required=True,
                                           label=_("input variable"))

    variable_list = serializers.ListField(required=True,
                                          label=_("Split variables"))

    model_params_setting = serializers.DictField(required=False,
                                                 label=_("Model parameter settings"))

    model_id = serializers.CharField(required=True, label=_("Model id"))


class IParameterExtractionNode(INode):
    type = 'parameter-extraction-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return VariableSplittingNodeParamsSerializer

    def _run(self):
        input_variable = self.workflow_manage.get_reference_field(
            self.node_params_serializer.data.get('input_variable')[0],
            self.node_params_serializer.data.get('input_variable')[1:])
        return self.execute(input_variable, self.node_params_serializer.data['variable_list'],
                            self.node_params_serializer.data['model_params_setting'],
                            self.node_params_serializer.data['model_id'])

    def execute(self, input_variable, variable_list, model_params_setting, model_id, **kwargs) -> NodeResult:
        pass
