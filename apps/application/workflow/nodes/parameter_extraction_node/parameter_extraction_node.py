# coding=utf-8
"""
    @project: MaxKB
    @file： parameter_extraction_node.py
    @desc:
"""
import json
import re

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from models_provider.models import Model
from models_provider.tools import get_model_instance_by_model_workspace_id, get_model_credential

prompt = """
Please strictly process the text according to the following requirements:
**Task**: 
Extract specified field information from given text

**Enter text**: 
{{question}}

**Extract configuration**: 
{{properties}}

**Rule**:
- Strictly follow the data and field of Extract configuration
- If not found, use null value
- Only return pure JSON without additional text
- Keep the string format neat
"""


class ParameterExtractionNodeSerializer(serializers.Serializer):
    input_variable = serializers.ListField(required=True, label=_("input variable"))
    variable_list = serializers.ListField(required=True, label=_("Split variables"))
    model_params_setting = serializers.DictField(required=False, label=_("Model parameter settings"))
    model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Model id"))
    model_id_type = serializers.CharField(required=False, default='custom', label=_("Model id type"))
    model_id_reference = serializers.ListField(required=False, child=serializers.CharField(), allow_empty=True,
                                               label=_("Reference Field"))


def _get_default_model_params_setting(model_id):
    model = QuerySet(Model).filter(id=model_id).first()
    credential = get_model_credential(model.provider, model.model_type, model.model_name)
    model_params_setting = credential.get_model_params_setting_form(model.model_name).get_default_form_data()
    return model_params_setting


def _generate_properties(variable_list):
    return {variable['field']: {'type': variable['parameter_type'], 'description': (variable.get('desc') or ""),
                                'title': variable['label']} for variable in variable_list}


def _generate_example(variable_list):
    return {variable['field']: None for variable in variable_list}


def _generate_content(input_variable, variable_list):
    properties = _generate_properties(variable_list)
    prompt_template = PromptTemplate.from_template(prompt, template_format='jinja2')
    value = prompt_template.format(properties=properties, question=input_variable)
    return value


def _json_loads(response, variable_list):
    if not response or not isinstance(response, str):
        return _generate_example(variable_list)

    cleaned = response.strip()

    extraction_strategies = [
        lambda: json.loads(cleaned),
        lambda: json.loads(re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned, re.DOTALL).group(1)),
        lambda: json.loads(re.search(r'(\{.*\})', cleaned, flags=re.DOTALL).group(1)),
    ]
    for strategy in extraction_strategies:
        try:
            result = strategy()
            return result
        except:
            continue
    return _generate_example(variable_list)


class ParameterExtractionNode(INode):
    serializer_class = ParameterExtractionNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = 'parameter-extraction-node'

    def execute(self):
        node_params = self.get_parameters()
        workflow_params = self.get_workflow_parameters()

        model_id = node_params.get('model_id')
        model_id_type = node_params.get('model_id_type', 'custom')
        model_id_reference = node_params.get('model_id_reference')
        model_params_setting = node_params.get('model_params_setting')
        input_variable_ref = node_params.get('input_variable')
        variable_list = node_params.get('variable_list')

        if model_id_type == 'reference' and model_id_reference:
            reference_data = self.workflow_manage.get_reference_field(
                model_id_reference[0], model_id_reference[1:],
            )
            if reference_data and isinstance(reference_data, dict):
                model_id = reference_data.get('model_id', model_id)
                model_params_setting = reference_data.get('model_params_setting')

        if not model_id:
            raise Exception(_('Model is not allowed to be empty'))

        if model_params_setting is None and model_id:
            model_params_setting = _get_default_model_params_setting(model_id)

        workspace_id = workflow_params.get('workspace_id')
        chat_model = get_model_instance_by_model_workspace_id(model_id, workspace_id,
                                                              **(model_params_setting or {}))

        input_variable = self.workflow_manage.get_reference_field(
            input_variable_ref[0], input_variable_ref[1:])

        input_variable_str = str(input_variable)
        self.write_context('request', input_variable_str)

        content = _generate_content(input_variable_str, variable_list)
        response = chat_model.invoke([HumanMessage(content=content)])
        result = _json_loads(response.content, variable_list)

        self.write_context('result', result)
        for key, value in result.items():
            self.write_context(key, value)
