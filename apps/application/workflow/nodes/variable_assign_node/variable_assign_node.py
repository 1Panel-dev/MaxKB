# coding=utf-8
"""
@project: MaxKB
@Author: 虎虎虎
@file: variable_assign_node.py
@desc: 变量赋值节点
"""

import json
from typing import Callable, List

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode

# 可赋值的变量分组:全局变量 / 会话变量 / 循环变量 / 输出变量
ASSIGNABLE_GROUPS = ("global", "chat", "loop", "output")


class VariableAssignNodeParamsSerializer(serializers.Serializer):
    variable_list = serializers.ListField(required=True, label=_("Reference Field"))


class VariableAssignNode(INode):
    serializer_class = VariableAssignNodeParamsSerializer
    supported_workflow_type_list = [
        WorkflowType.APPLICATION,
        WorkflowType.KNOWLEDGE,
        WorkflowType.TOOL,
    ]
    type = "variable-assign-node"

    def execute(self):
        node_params = self.get_parameters()
        result_list = []
        for variable in node_params.get("variable_list", []):
            if not variable.get("fields"):
                continue

            if variable["fields"][0] in ASSIGNABLE_GROUPS:
                result_list.append(self.handle(variable, self.evaluation))

        self.write_context("variable_list", node_params.get("variable_list", []))
        self.write_context("result_list", result_list)

    def evaluation(self, variable, value):
        # 写到哪一层由 workflow_manage 决定:循环体内的 global/chat/output 会逐级交给根工作流,loop 写到所属循环
        self.workflow_manage.write_context(variable["fields"][0], variable["fields"][1], value)

    def handle(self, variable, evaluation: Callable):
        result = {
            "name": variable["name"],
            "input_value": self.get_reference_content(variable["fields"]),
        }
        if variable["source"] == "custom":
            if variable["type"] == "json":
                if isinstance(variable["value"], dict) or isinstance(variable["value"], list):
                    val = variable["value"]
                else:
                    val = json.loads(variable["value"])
                evaluation(variable, val)
                result["output_value"] = variable["value"] = val
            elif variable["type"] == "string":
                # 变量解析 例如：{{global.xxx}}
                val = self.workflow_manage.generate_prompt(variable["value"])
                evaluation(variable, val)
                result["output_value"] = val
            else:
                val = variable["value"]
                evaluation(variable, val)
                result["output_value"] = val
        elif variable["source"] == "referencing":
            reference = self.get_reference_content(variable["reference"])
            evaluation(variable, reference)
            result["output_value"] = reference
        else:
            val = None
            evaluation(variable, val)
            result["output_value"] = val

        # 获取输入输出值的类型，用于显示在执行详情页面中
        result["input_type"] = (
            type(result.get("input_value")).__name__ if result.get("input_value") is not None else "null"
        )
        result["output_type"] = (
            type(result.get("output_value")).__name__ if result.get("output_value") is not None else "null"
        )

        return result

    def get_reference_content(self, fields: List[str]):
        return self.workflow_manage.get_reference_field(fields[0], fields[1:]) if fields else None

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "variable_list": self.get_context("variable_list"),
                "result_list": self.get_context("result_list"),
                "status": self.status.value if self.status else None,
            }
        )
        return details
