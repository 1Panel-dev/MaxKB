# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： base_loop_continue_node.py
    @date：2025/9/15 12:13
    @desc:
"""
from application.flow.compare import do_assertion
from application.flow.i_step_node import NodeResult
from application.flow.step_node.loop_continue_node.i_loop_continue_node import ILoopContinueNode


class BaseLoopContinueNode(ILoopContinueNode):
    def save_context(self, details, workflow_manage):
        self.context['exception_message'] = details.get('err_message')

    def execute(self, condition, condition_list, **kwargs) -> NodeResult:
        is_continue = do_assertion(self.workflow_manage, condition, condition_list)
        self.context['is_continue'] = is_continue
        if is_continue:
            return NodeResult({'is_continue': is_continue, 'branch_id': 'continue'}, {})
        return NodeResult({'is_continue': is_continue}, {})

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            "is_continue": self.context.get('is_continue'),
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message,
            'enableException': self.node.properties.get('enableException'),
        }
