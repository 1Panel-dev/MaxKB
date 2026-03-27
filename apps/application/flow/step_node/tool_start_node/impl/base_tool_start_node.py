# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_start_node.py
    @date：2024/6/3 17:17
    @desc:
"""
from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import NodeResult
from application.flow.step_node.tool_start_node.i_tool_start_node import IToolStartNode


class BaseToolStartStepNode(IToolStartNode):
    def save_context(self, details, workflow_manage):
        base_node = self.workflow_manage.get_base_node()
        workflow_variable = {}
        self.context['exception_message'] = details.get('err_message')
        self.status = details.get('status')
        self.err_message = details.get('err_message')
        for key, value in workflow_variable.items():
            workflow_manage.context[key] = value
        for item in details.get('global_fields', []):
            workflow_manage.context[item.get('key')] = item.get('value')

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        pass

    def execute(self, **kwargs) -> NodeResult:
        base_node = self.workflow_manage.get_base_node()
        global_value = {}
        params = self.workflow_manage.get_body()
        for item in base_node.properties.get('user_input_field_list', []):
            global_value[item.get('field')] = params.get(item.get('field'))

        self.workflow_manage.out_context = {
            item.get('field'): None
            for item in base_node.properties.get('user_output_field_list', [])
            if item.get('default_value', None) is not None
        }
        return NodeResult({}, global_value)

    def get_details(self, index: int, **kwargs):
        global_fields = []
        for field in self.node.properties.get('config')['globalFields']:
            key = field['value']
            global_fields.append({
                'label': field.get('label'),
                'key': key,
                'value': self.workflow_manage.context[key] if key in self.workflow_manage.context else ''
            })
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            "question": self.context.get('question'),
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message,
            'global_fields': global_fields,
            '': '',
            'enableException': self.node.properties.get('enableException'),
        }
