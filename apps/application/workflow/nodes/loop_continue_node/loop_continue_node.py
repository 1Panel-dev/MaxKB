# coding=utf-8
"""
@project: MaxKB
@Author：虎虎虎
@file： loop_continue_node.py
@date：2026/7/6 15:10
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


class LoopContinueNodeSerializer(serializers.Serializer):
    condition = serializers.CharField(required=True, label=_("Condition or|and"))
    condition_list = ConditionSerializer(many=True)


class LoopContinueNode(INode):
    serializer_class = LoopContinueNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = "loop-continue-node"

    def execute(self):
        node_params = self.get_parameters()
        condition = node_params.get("condition")
        condition_list = node_params.get("condition_list", [])

        is_continue = do_assertion(self.workflow_manage, condition, condition_list)
        self.write_context("is_continue", is_continue)

        if is_continue:
            self.complete(Status.SUCCESS, signal=Signal.CONTINUE)
            return
        self.complete(Status.SUCCESS)

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "is_continue": self.get_context("is_continue"),
            }
        )
        return details
