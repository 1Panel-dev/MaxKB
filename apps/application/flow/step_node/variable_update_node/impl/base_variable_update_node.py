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
from application.flow.step_node.variable_update_node.i_variable_update_node import IVariableUpdateNode


class BaseVariableUpdateNode(IVariableUpdateNode):
    def execute(self, value_type, stream, fields=None, content=None, target_value=None, **kwargs) -> NodeResult:
        if value_type == 'referencing':
            target_val = self.get_reference_content(target_value)
        else:
            target_val = self.generate_customized_content(content)

        self.set_reference_content(fields, target_val)
        return NodeResult({'result': f'{fields[1]} = {target_val}'}, {fields[1]: target_val})

    def generate_customized_content(self, prompt):
        return self.workflow_manage.generate_prompt(prompt)

    # 获取参数的值
    def get_reference_content(self, fields: List[str]):
        return str(self.workflow_manage.get_reference_field(
            fields[0],
            fields[1:]))

    def set_reference_content(self, fields: List[str], target_value: str):
        self.workflow_manage.set_reference_field(fields[0], fields, target_value)
        return

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'result': self.context.get('result'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message
        }
