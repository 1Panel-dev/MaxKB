# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： loop_start_node.py
    @date：2026/7/2 10:00
    @desc:
"""
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode


class LoopStartNodeSerializer(serializers.Serializer):
    pass


class LoopStartNode(INode):
    serializer_class = LoopStartNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = 'loop-start-node'

    def execute(self):
        loop_context = getattr(self.workflow_manage, 'loop_context', {})
        index = loop_context.get('index', 0)
        item = loop_context.get('item', None)

        self.write_context('index', index)
        self.write_context('item', item)
