# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： i_start_node.py
    @date：2024/6/3 16:54
    @desc:
"""

from application.flow.i_step_node import INode, NodeResult


class ILoopStarNode(INode):
    type = 'loop-start-node'

    def _run(self):
        return self.execute(**self.flow_params_serializer.data)

    def execute(self,  **kwargs) -> NodeResult:
        pass
