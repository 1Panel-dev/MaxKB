# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_condition_node.py
    @date：2024/6/7 11:29
    @desc:
"""
from typing import List

from application.flow.i_step_node import NodeResult
from application.flow.compare import do_assertion
from application.flow.step_node.condition_node.i_condition_node import IConditionNode


class BaseConditionNode(IConditionNode):
    def save_context(self, details, workflow_manage):
        self.context['branch_id'] = details.get('branch_id')
        self.context['branch_name'] = details.get('branch_name')
        self.context['exception_message'] = details.get('err_message')

    def execute(self, **kwargs) -> NodeResult:
        branch_list = self.node_params_serializer.data['branch']
        branch = self._execute(branch_list)
        r = NodeResult({'branch_id': branch.get('id'), 'branch_name': branch.get('type')}, {})
        return r

    def _execute(self, branch_list: List):
        for branch in branch_list:
            if self.branch_assertion(branch):
                return branch

    def branch_assertion(self, branch):
        return do_assertion(self.workflow_manage, branch.get('condition'), branch.get('conditions'))

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'branch_id': self.context.get('branch_id'),
            'branch_name': self.context.get('branch_name'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message,
            'enableException': self.node.properties.get('enableException'),
        }
