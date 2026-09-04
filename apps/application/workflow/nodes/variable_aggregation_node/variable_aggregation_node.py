# coding=utf-8
"""
@project: MaxKB
@Author: 虎虎虎
@file: variable_aggregation_node.py
@desc: 变量聚合节点
"""

from typing import Callable, List

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode


class VariableListSerializer(serializers.Serializer):
    v_id = serializers.CharField(required=True, label=_("Variable id"))
    key = serializers.CharField(required=False, label=_("Key"), allow_null=True, allow_blank=True)
    variable = serializers.ListField(required=True, label=_("Variable"))


class VariableGroupSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, label=_("Group id"))
    field = serializers.CharField(required=True, label=_("group_name"))
    label = serializers.CharField(required=True)
    variable_list = VariableListSerializer(many=True)


class VariableAggregationNodeSerializer(serializers.Serializer):
    strategy = serializers.CharField(required=True, label=_("Strategy"))
    group_list = VariableGroupSerializer(many=True)


def _filter_file_bytes(data):
    """递归过滤掉所有层级的 file_bytes"""
    if isinstance(data, dict):
        return {k: _filter_file_bytes(v) for k, v in data.items() if k != "file_bytes"}
    elif isinstance(data, list):
        return [_filter_file_bytes(item) for item in data]
    else:
        return data


class VariableAggregationNode(INode):
    serializer_class = VariableAggregationNodeSerializer
    supported_workflow_type_list = [
        WorkflowType.APPLICATION,
        WorkflowType.KNOWLEDGE,
        WorkflowType.TOOL,
    ]
    type = "variable-aggregation-node"

    def execute(self):
        node_params = self.get_parameters()
        strategy = node_params.get("strategy")
        group_list = node_params.get("group_list", [])

        strategy_map = {
            "first_non_null": self.get_first_non_null,
            "variable_to_array": self.set_variable_to_array,
            "variable_to_dict": self.set_variable_to_dict,
        }

        # 向下兼容
        if strategy == "variable_to_json":
            strategy = "variable_to_array"

        result = {
            item.get("field"): strategy_map[strategy](item.get("variable_list")) if item.get("variable_list") else []
            for item in group_list
        }

        self.write_context("result", result)
        self.write_context("strategy", strategy)
        self.write_context("group_list", self.reset_group_list(group_list))
        for key, value in result.items():
            self.write_context(key, value)

    def get_first_non_null(self, variable_list) -> Callable:
        for variable in variable_list:
            v = self.get_reference_content(variable.get("variable"))
            if v is not None and not (isinstance(v, (str, list, dict)) and len(v) == 0):
                return v
        return None

    def set_variable_to_array(self, variable_list) -> List:
        return [self.get_reference_content(variable.get("variable")) for variable in variable_list]

    def set_variable_to_dict(self, variable_list) -> dict:
        return {
            (variable.get("key") or variable.get("variable")[-1]): self.get_reference_content(variable.get("variable"))
            for variable in variable_list
        }

    def reset_variable(self, variable):
        value = self.get_reference_content(variable.get("variable"))
        node_id = variable.get("variable")[0]
        node = self.workflow_manage.workflow.get_node(node_id)
        return {
            "value": value,
            "node_name": node.properties.get("stepName") if node is not None else node_id,
            "field": variable.get("variable")[1],
        }

    def reset_group_list(self, group_list):
        return [
            {
                "label": g.get("label"),
                "variable_list": [self.reset_variable(variable) for variable in g.get("variable_list")],
            }
            for g in group_list
        ]

    def get_reference_content(self, variable):
        return (
            self.workflow_manage.get_reference_field(variable[0], variable[1:])
            if variable and len(variable) >= 2
            else None
        )

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "result": _filter_file_bytes(self.get_context("result")),
                "strategy": self.get_context("strategy"),
                "group_list": _filter_file_bytes(self.get_context("group_list")),
                "status": self.status.value if self.status else None,
            }
        )
        return details
