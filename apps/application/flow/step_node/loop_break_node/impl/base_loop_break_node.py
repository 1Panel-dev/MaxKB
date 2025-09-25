# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： base_loop_break_node.py
    @date：2025/9/15 12:17
    @desc:
"""
import time
from typing import List, Dict

from application.flow.compare import compare_handle_list
from application.flow.i_step_node import NodeResult
from application.flow.step_node.loop_break_node.i_loop_break_node import ILoopBreakNode


def _write_context(step_variable: Dict, global_variable: Dict, node, workflow):
    if step_variable.get("is_break"):
        yield "BREAK"

    node.context['run_time'] = time.time() - node.context['start_time']


class BaseLoopBreakNode(ILoopBreakNode):
    def execute(self, condition, condition_list, **kwargs) -> NodeResult:
        r = [self.assertion(row.get('field'), row.get('compare'), row.get('value')) for row in
             condition_list]
        is_break = all(r) if condition == 'and' else any(r)
        if is_break:
            self.node_params['is_result'] = True
        self.context['is_break'] = is_break
        return NodeResult({'is_break': is_break}, {},
                          _write_context=_write_context,
                          _is_interrupt=lambda n, v, w: is_break)

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
            'is_break': self.context.get('is_break'),
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message
        }
