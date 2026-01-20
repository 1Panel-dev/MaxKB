# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_reply_node.py
    @date：2024/6/11 17:25
    @desc:
"""
from typing import List

from application.flow.i_step_node import NodeResult
from application.flow.step_node.direct_reply_node.i_reply_node import IReplyNode


class BaseReplyNode(IReplyNode):
    def save_context(self, details, workflow_manage):
        self.context['answer'] = details.get('answer')
        self.context['exception_message'] = details.get('err_message')
        if self.node_params.get('is_result', False):
            self.answer_text = details.get('answer')

    def execute(self, reply_type, stream, fields=None, content=None, **kwargs) -> NodeResult:
        if reply_type == 'referencing':
            result = self.get_reference_content(fields)
        else:
            result = self.generate_reply_content(content)
        return NodeResult({'answer': result}, {})

    def generate_reply_content(self, prompt):
        return self.workflow_manage.generate_prompt(prompt)

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
            'answer': self.context.get('answer'),
            'status': self.status,
            'err_message': self.err_message,
            'enableException': self.node.properties.get('enableException'),
        }
