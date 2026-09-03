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
from application.workflow.loop_workflow_manage import LoopWorkFlowManage


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

            field0 = variable["fields"][0]
            if field0 == "global":
                result = self.handle(variable, self.global_evaluation)
                result_list.append(result)
            elif field0 == "chat":
                result = self.handle(variable, self.chat_evaluation)
                result_list.append(result)
            elif field0 == "loop":
                result = self.handle(variable, self.loop_evaluation)
                result_list.append(result)
            elif field0 == "output":
                result = self.handle(variable, self.output_evaluation)
                result_list.append(result)

        self.write_context("variable_list", node_params.get("variable_list", []))
        self.write_context("result_list", result_list)

    def _target_manage(self):
        return (
            self.workflow_manage.parent_workflow_manage
            if isinstance(self.workflow_manage, LoopWorkFlowManage)
            else self.workflow_manage
        )

    def global_evaluation(self, variable, value):
        self._target_manage().write_context("global", variable["fields"][1], value)

    def loop_evaluation(self, variable, value):
        self.workflow_manage.write_context("loop", variable["fields"][1], value)

    def chat_evaluation(self, variable, value):
        self._target_manage().write_context("chat", variable["fields"][1], value)

    def output_evaluation(self, variable, value):
        self._target_manage().write_context("output", variable["fields"][1], value)

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
