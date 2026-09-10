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
    type = "loop-start-node"

    def execute(self):
        loop = self.workflow_manage.context.get("loop")
        if loop is None:
            self.write_context("loop", {})
        parameters = self.workflow_manage.get_parameters()
        if parameters is not None:
            index = parameters.get("index", 0)
            item = parameters.get("item", 0)
            self.write_context("index", index)
            self.write_context("item", item)
        else:
            self.write_context("index", 0)
            self.write_context("item", 0)

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "index": self.get_context("index"),
                "item": self.get_context("item"),
            }
        )
        return details
