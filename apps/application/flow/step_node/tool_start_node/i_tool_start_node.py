# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： i_start_node.py
    @date：2024/6/3 16:54
    @desc:
"""
from application.flow.common import WorkflowMode
from application.flow.i_step_node import INode, NodeResult


class IToolStartNode(INode):
    type = 'tool-start-node'
    support = [WorkflowMode.TOOL]

    def _run(self):
        return self.execute(**self.flow_params_serializer.data)

    def execute(self, **kwargs) -> NodeResult:
        pass
