# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_start_node.py
    @date：2024/6/3 17:17
    @desc:
"""
import time
from datetime import datetime

from application.flow.i_step_node import NodeResult
from application.flow.step_node.start_node.i_start_node import IStarNode


class BaseStartStepNode(IStarNode):
    def execute(self, question, **kwargs) -> NodeResult:
        """
        开始节点 初始化全局变量
        """
        return NodeResult({'question': question},
                          {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'start_time': time.time()})

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            "question": self.context.get('question'),
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message
        }
