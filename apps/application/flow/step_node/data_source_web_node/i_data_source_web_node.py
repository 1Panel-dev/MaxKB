# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： i_data_source_web_node.py
    @date：2025/11/12 13:47
    @desc:
"""
from abc import abstractmethod

from application.flow.common import WorkflowMode
from application.flow.i_step_node import INode, NodeResult


class IDataSourceWebNode(INode):
    type = 'data-source-web-node'
    support = [WorkflowMode.KNOWLEDGE]

    @staticmethod
    @abstractmethod
    def get_form_list(node):
        pass

    def _run(self):
        return self.execute(**self.flow_params_serializer.data)

    def execute(self, **kwargs) -> NodeResult:
        pass
