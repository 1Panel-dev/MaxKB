# coding=utf-8
from typing import List

from application.flow.i_step_node import NodeResult
from application.flow.step_node.variable_assign.i_variable_assign_node import IVariableAssignNode


class BaseVariableAssignNode(IVariableAssignNode):
    def save_context(self, details, workflow_manage):
        self.context['variable_list'] = details.get('variable_list')

    def execute(self, variable_list, stream, **kwargs) -> NodeResult:
        #
        for variable in variable_list:
            if 'fields' not in variable:
                continue
            if 'global' == variable['fields'][0]:
                if variable['source'] == 'custom':
                    self.workflow_manage.context[variable['fields'][1]] = variable['value']
                else:
                    reference = self.get_reference_content(variable['reference'])
                    self.workflow_manage.context[variable['fields'][1]] = reference
        # print('variable_list:', variable_list)

        return NodeResult({'variable_list': variable_list}, {})

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
            'status': self.status,
            'err_message': self.err_message
        }
