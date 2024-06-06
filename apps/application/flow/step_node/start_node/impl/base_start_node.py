# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_start_node.py
    @date：2024/6/3 17:17
    @desc:
"""
import time

from application.flow.i_step_node import NodeResult
from application.flow.step_node.start_node.i_start_node import IStarNode


class BaseStartStepNode(IStarNode):
    def execute(self, question, **kwargs) -> NodeResult:
        """
        开始节点 初始化全局变量
        """
        return NodeResult({'question': question}, {'time': time.time()})
