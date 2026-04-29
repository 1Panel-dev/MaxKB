# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： base_loop_break_node.py
    @date：2025/9/15 12:17
    @desc:
"""
import time
from typing import Dict

from application.flow.compare import do_assertion
from application.flow.i_step_node import NodeResult
from application.flow.step_node.loop_break_node.i_loop_break_node import ILoopBreakNode


def _write_context(step_variable: Dict, global_variable: Dict, node, workflow):
    if step_variable.get("is_break"):
        yield "BREAK"

    node.context['run_time'] = time.time() - node.context['start_time']


class BaseLoopBreakNode(ILoopBreakNode):
    def save_context(self, details, workflow_manage):
        self.context['exception_message'] = details.get('err_message')

    def execute(self, condition, condition_list, **kwargs) -> NodeResult:
        is_break = do_assertion(self.workflow_manage, condition, condition_list)
        if is_break:
            self.node_params['is_result'] = True
        self.context['is_break'] = is_break
        return NodeResult({'is_break': is_break}, {},
                          _write_context=_write_context,
                          _is_interrupt=lambda n, v, w: is_break)

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'is_break': self.context.get('is_break'),
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message,
            'enableException': self.node.properties.get('enableException'),
        }
