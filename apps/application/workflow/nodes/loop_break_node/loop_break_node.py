# coding=utf-8
"""
@project: MaxKB
@Author：虎虎虎
@file： loop_break_node.py
@date：2026/7/6 15:00
@desc:
"""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.workflow.compare import do_assertion
from application.workflow.common import WorkflowType
from application.workflow.i_node import INode, Signal
from application.workflow.status import Status


class ConditionSerializer(serializers.Serializer):
    compare = serializers.CharField(required=True, label=_("Comparator"))
    value = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_("value"))
    field = serializers.ListField(required=True, label=_("Fields"))


class LoopBreakNodeSerializer(serializers.Serializer):
    condition = serializers.CharField(required=True, label=_("Condition or|and"))
    condition_list = ConditionSerializer(many=True)


class LoopBreakNode(INode):
    serializer_class = LoopBreakNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = "loop-break-node"

    def execute(self):
        node_params = self.get_parameters()
        condition = node_params.get("condition")
        condition_list = node_params.get("condition_list", [])

        is_break = do_assertion(self.workflow_manage, condition, condition_list)
        self.write_context("is_break", is_break)

        if is_break:
            self.complete(Status.SUCCESS, signal=Signal.BREAK)
            return
        self.complete(Status.SUCCESS)

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "is_break": self.get_context("is_break"),
            }
        )
        return details
