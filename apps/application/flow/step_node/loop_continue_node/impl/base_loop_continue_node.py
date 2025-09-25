# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： base_loop_continue_node.py
    @date：2025/9/15 12:13
    @desc:
"""
from typing import List

from application.flow.compare import compare_handle_list
from application.flow.i_step_node import NodeResult
from application.flow.step_node.loop_continue_node.i_loop_continue_node import ILoopContinueNode


class BaseLoopContinueNode(ILoopContinueNode):
    def execute(self, condition, condition_list, **kwargs) -> NodeResult:
        condition_list = [self.assertion(row.get('field'), row.get('compare'), row.get('value')) for row in
                          condition_list]
        is_continue = all(condition_list) if condition == 'and' else any(condition_list)
        self.context['is_continue'] = is_continue
        if is_continue:
            return NodeResult({'is_continue': is_continue, 'branch_id': 'continue'}, {})
        return NodeResult({'is_continue': is_continue}, {})

    def assertion(self, field_list: List[str], compare: str, value):
        try:
            value = self.workflow_manage.generate_prompt(value)
        except Exception as e:
            pass
        field_value = None
        try:
            field_value = self.workflow_manage.get_reference_field(field_list[0], field_list[1:])
        except  Exception as e:
            pass
        for compare_handler in compare_handle_list:
            if compare_handler.support(field_list[0], field_list[1:], field_value, compare, value):
                return compare_handler.compare(field_value, compare, value)

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            "is_continue": self.context.get('is_continue'),
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message
        }
