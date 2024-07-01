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
from application.flow.step_node.condition_node.compare import compare_handle_list
from application.flow.step_node.condition_node.i_condition_node import IConditionNode


class BaseConditionNode(IConditionNode):
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
        condition_list = [self.assertion(row.get('field'), row.get('compare'), row.get('value')) for row in
                          branch.get('conditions')]
        condition = branch.get('condition')
        return all(condition_list) if condition == 'and' else any(condition_list)

    def assertion(self, field_list: List[str], compare: str, value):
        field_value = self.workflow_manage.get_reference_field(field_list[0], field_list[1:])
        for compare_handler in compare_handle_list:
            if compare_handler.support(field_list[0], field_list[1:], field_value, compare, value):
                return compare_handler.compare(field_value, compare, value)

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'branch_id': self.context.get('branch_id'),
            'branch_name': self.context.get('branch_name'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message
        }
