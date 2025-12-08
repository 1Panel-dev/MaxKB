# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： base_variable_splitting_node.py
    @date：2025/10/13 15:02
    @desc:
"""
import json
import re

from django.db.models import QuerySet
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate

from application.flow.i_step_node import NodeResult
from application.flow.step_node.parameter_extraction_node.i_parameter_extraction_node import IParameterExtractionNode
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


def get_default_model_params_setting(model_id):
    model = QuerySet(Model).filter(id=model_id).first()
    credential = get_model_credential(model.provider, model.model_type, model.model_name)
    model_params_setting = credential.get_model_params_setting_form(
        model.model_name).get_default_form_data()
    return model_params_setting


def generate_properties(variable_list):
    return {variable['field']: {'type': variable['parameter_type'], 'description': (variable.get('desc') or ""),
                                'title': variable['label']} for variable in
            variable_list}


def generate_example(variable_list):
    return {variable['field']: None for variable in variable_list}


def generate_content(input_variable, variable_list):
    properties = generate_properties(variable_list)
    prompt_template = PromptTemplate.from_template(prompt, template_format='jinja2')
    value = prompt_template.format(properties=properties, question=input_variable)
    return value


def json_loads(response, expected_fields):
    if not response or not isinstance(response, str):
        return {field: None for field in expected_fields}

    cleaned = response.strip()

    extraction_strategies = [
        lambda: json.loads(cleaned),
        lambda: json.loads(re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned, re.DOTALL).group(1)),
        lambda: json.loads(re.search(r'(\{[\s\S]*\})', cleaned).group(1)),
    ]
    for strategy in extraction_strategies:
        try:
            result = strategy()
            return result
        except:
            continue
    return generate_example(expected_fields)


class BaseParameterExtractionNode(IParameterExtractionNode):

    def save_context(self, details, workflow_manage):
        for key, value in details.get('result').items():
            self.context[key] = value
        self.context['result'] = details.get('result')
        self.context['request'] = details.get('request')

    def execute(self, input_variable, variable_list, model_params_setting, model_id, **kwargs) -> NodeResult:
        input_variable = str(input_variable)
        self.context['request'] = input_variable
        if model_params_setting is None:
            model_params_setting = get_default_model_params_setting(model_id)
        workspace_id = self.workflow_manage.get_body().get('workspace_id')
        chat_model = get_model_instance_by_model_workspace_id(model_id, workspace_id,
                                                              **model_params_setting)
        content = generate_content(input_variable, variable_list)
        response = chat_model.invoke([HumanMessage(content=content)])
        result = json_loads(response.content, variable_list)
        return NodeResult({'result': result, **result}, {})

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'request': self.context.get('request'),
            'result': self.context.get('result'),
            'status': self.status,
            'err_message': self.err_message
        }
