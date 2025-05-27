# coding=utf-8
import json
from typing import List

from application.flow.i_step_node import NodeResult
from application.flow.step_node.variable_assign_node.i_variable_assign_node import IVariableAssignNode


class BaseVariableAssignNode(IVariableAssignNode):
    def save_context(self, details, workflow_manage):
        self.context['variable_list'] = details.get('variable_list')
        self.context['result_list'] = details.get('result_list')

    def execute(self, variable_list, stream, **kwargs) -> NodeResult:
        #
        result_list = []
        for variable in variable_list:
            if 'fields' not in variable:
                continue
            if 'global' == variable['fields'][0]:
                result = {
                    'name': variable['name'],
                    'input_value': self.get_reference_content(variable['fields']),
                }
                if variable['source'] == 'custom':
                    if variable['type'] == 'json':
                        if isinstance(variable['value'], dict) or isinstance(variable['value'], list):
                            val = variable['value']
                        else:
                            val = json.loads(variable['value'])
                        self.workflow_manage.context[variable['fields'][1]] = val
                        result['output_value'] = variable['value'] = val
                    elif variable['type'] == 'string':
                        # 变量解析 例如：{{global.xxx}}
                        val = self.workflow_manage.generate_prompt(variable['value'])
                        self.workflow_manage.context[variable['fields'][1]] = val
                        result['output_value'] = val
                    else:
                        val = variable['value']
                        self.workflow_manage.context[variable['fields'][1]] = val
                        result['output_value'] = val
                else:
                    reference = self.get_reference_content(variable['reference'])
                    self.workflow_manage.context[variable['fields'][1]] = reference
                    result['output_value'] = reference
                result_list.append(result)

        return NodeResult({'variable_list': variable_list, 'result_list': result_list}, {})

    def get_reference_content(self, fields: List[str]):
        return str(self.workflow_manage.get_reference_field(
            fields[0],
            fields[1:]))

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'variable_list': self.context.get('variable_list'),
            'result_list': self.context.get('result_list'),
            'status': self.status,
            'err_message': self.err_message
        }
