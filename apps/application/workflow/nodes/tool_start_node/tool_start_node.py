# coding=utf-8
"""
@project:  MaxKB
@Author:   虎虎虎
@file:     tool_start_node.py
@date:     2026/9/3 17:20
@desc:     工具工作流的起始节点，负责把工具入参写入全局变量、初始化输出字段
"""

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode


class ToolStartNode(INode):
    supported_workflow_type_list = [WorkflowType.TOOL]
    type = "tool-start-node"

    def execute(self):
        workflow_params = self.get_workflow_parameters()
        base_node = self.workflow_manage.workflow.get_node("tool-base-node")
        user_input_field_list = base_node.properties.get("user_input_field_list", []) if base_node else []
        user_output_field_list = base_node.properties.get("user_output_field_list", []) if base_node else []

        # 入参 -> 全局变量（引用约定 global.<field>）
        for item in user_input_field_list:
            field = item.get("field")
            self.workflow_manage.write_context("global", field, workflow_params.get(field))

        # 初始化输出字段默认值 -> output（工作流内由变量赋值节点覆写）
        for item in user_output_field_list:
            if item.get("default_value", None) is not None:
                self.workflow_manage.write_context("output", item.get("field"), item.get("default_value"))

        self.write_context("question", workflow_params.get("question", ""))

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        global_fields = []
        for field in (self.node.properties.get("config") or {}).get("globalFields", []) or []:
            key = field.get("value")
            global_fields.append(
                {
                    "label": field.get("label"),
                    "key": key,
                    "value": self.workflow_manage.get_context("global", key) or "",
                }
            )
        details.update(
            {
                "question": self.get_context("question"),
                "global_fields": global_fields,
            }
        )
        return details
