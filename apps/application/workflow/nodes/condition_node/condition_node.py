# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： condition_node.py
    @date：2026/7/2 10:00
    @desc:
"""
from typing import List

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.workflow.compare import do_assertion
from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from application.workflow.status import Status


class ConditionSerializer(serializers.Serializer):
    compare = serializers.CharField(required=True, label=_("Comparator"))
    value = serializers.CharField(required=True, label=_("value"))
    field = serializers.ListField(required=True, label=_("Fields"))


class ConditionBranchSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, label=_("Branch id"))
    type = serializers.CharField(required=True, label=_("Branch Type"))
    condition = serializers.CharField(required=True, label=_("Condition or|and"))
    conditions = ConditionSerializer(many=True)


class ConditionNodeSerializer(serializers.Serializer):
    branch = ConditionBranchSerializer(many=True)


class ConditionNode(INode):
    serializer_class = ConditionNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = 'condition-node'

    def execute(self):
        node_params = self.get_parameters()
        branch_list = node_params.get('branch', [])
        branch = self._evaluate_branches(branch_list)
        branch_id = branch.get('id')
        branch_name = branch.get('type')

        self.write_context('branch_id', branch_id)
        self.write_context('branch_name', branch_name)

        self.complete(Status.SUCCESS, [self.branch_anchor(branch_id)])

    def _evaluate_branches(self, branch_list: List):
        for branch in branch_list:
            if self._branch_assertion(branch):
                return branch
        return branch_list[-1] if branch_list else {}

    def _branch_assertion(self, branch):
        return do_assertion(
            self.workflow_manage,
            branch.get('condition'),
            branch.get('conditions')
        )
