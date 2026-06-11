# coding=utf-8
"""
    @project: MaxKB
    @Author：AI Assistant
    @file： i_empty_node.py
    @date：2026/06/10
    @desc: 空节点接口定义 - 用于流程判断的ELSE分支占位
"""
from typing import Type

from rest_framework import serializers

from application.flow.common import WorkflowMode
from application.flow.i_step_node import INode, NodeResult


class EmptyNodeParamsSerializer(serializers.Serializer):
    """空节点参数序列化器 - 无需任何参数"""
    
    def is_valid(self, *, raise_exception=False):
        # 空节点不需要验证任何参数，直接返回 True
        return True


class IEmptyNode(INode):
    """空节点接口"""
    type = 'empty-node'
    support = [WorkflowMode.APPLICATION, WorkflowMode.APPLICATION_LOOP, WorkflowMode.KNOWLEDGE_LOOP,
               WorkflowMode.KNOWLEDGE, WorkflowMode.TOOL, WorkflowMode.TOOL_LOOP]

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return EmptyNodeParamsSerializer

    def _run(self):
        return self.execute()

    def execute(self, **kwargs) -> NodeResult:
        """执行空节点 - 不产生任何输出"""
        return NodeResult({}, {})
