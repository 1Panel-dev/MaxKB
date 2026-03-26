# coding=utf-8

from typing import Type

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.common import WorkflowMode
from application.flow.i_step_node import INode, NodeResult


class VariableSplittingNodeParamsSerializer(serializers.Serializer):
    input_variable = serializers.ListField(required=True,
                                           label=_("input variable"))

    variable_list = serializers.ListField(required=True,
                                          label=_("Split variables"))

    model_params_setting = serializers.DictField(required=False,
                                                 label=_("Model parameter settings"))

    model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Model id"))
    model_id_type = serializers.CharField(required=False, default='custom', label=_("Model id type"))
    model_id_reference = serializers.ListField(required=False, child=serializers.CharField(), allow_empty=True,
                                               label=_("Reference Field"))


class IParameterExtractionNode(INode):
    type = 'parameter-extraction-node'
    support = [WorkflowMode.APPLICATION, WorkflowMode.APPLICATION_LOOP, WorkflowMode.KNOWLEDGE,
               WorkflowMode.KNOWLEDGE_LOOP, WorkflowMode.TOOL, WorkflowMode.TOOL_LOOP]

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return VariableSplittingNodeParamsSerializer

    def _run(self):
        model_id_type = self.node_params_serializer.data.get('model_id_type')
        model_id_reference = self.node_params_serializer.data.get('model_id_reference')
        model_id = self.node_params_serializer.data.get('model_id')
        model_params_setting = self.node_params_serializer.data.get('model_params_setting')
        # 处理引用类型
        if model_id_type == 'reference' and model_id_reference:
            reference_data = self.workflow_manage.get_reference_field(
                model_id_reference[0],
                model_id_reference[1:],
            )
            if reference_data and isinstance(reference_data, dict):
                model_id = reference_data.get('model_id', model_id)
                model_params_setting = reference_data.get('model_params_setting')

        input_variable = self.workflow_manage.get_reference_field(
            self.node_params_serializer.data.get('input_variable')[0],
            self.node_params_serializer.data.get('input_variable')[1:])
        return self.execute(input_variable, self.node_params_serializer.data['variable_list'],
                            model_params_setting, model_id)

    def execute(self, input_variable, variable_list, model_params_setting, model_id, **kwargs) -> NodeResult:
        pass
