# coding=utf-8
"""
@project: MaxKB
@Author：虎虎虎
@file： reply_node.py
@date：2026/7/2 10:00
@desc:
"""

import json
from typing import List

import uuid_utils.compat as uuid
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from application.workflow.message.struct.content import NodeInfo, Position
from application.workflow.message.struct.html_content import HtmlContent
from application.workflow.message.struct.text_content import TextContent
from application.workflow.message.struct.tool_content import ToolContent
from application.workflow.status import Status


class ReplyNodeSerializer(serializers.Serializer):
    reply_type = serializers.CharField(required=True, label=_("Response Type"))
    # 输出内容类型:TEXT 文本(默认) / HTML / TOOL 工具调用
    content_type = serializers.ChoiceField(
        required=False, default="TEXT", choices=["TEXT", "HTML", "TOOL"], label=_("Content Type")
    )
    fields = serializers.ListField(required=False, label=_("Reference Field"))
    content = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Direct answer content"))
    is_result = serializers.BooleanField(required=False, label=_("Whether to return content"))


def _to_text(value):
    return "" if value is None else str(value)


def _to_json_text(value):
    if value is None:
        return ""
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def _first(item: dict, *keys):
    for key in keys:
        if item.get(key) is not None:
            return item.get(key)
    return None


def _to_tool_list(value):
    """
    把工具回复内容归一化为工具调用列表。
    支持对象或对象数组(或其 JSON 字符串),元素字段:
    id 调用id(缺省自动生成) / name 函数名 / arguments 参数 / content 工具结果;
    同时兼容 toolName、functionArguments、function_name、function_arguments、result 写法。
    """
    if isinstance(value, str):
        try:
            value = json.loads(value) if value.strip() else []
        except ValueError:
            raise Exception(_("Tool reply content must be a JSON object or array"))
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        raise Exception(_("Tool reply content must be a JSON object or array"))
    return [
        {
            "id": _to_text(item.get("id")) or str(uuid.uuid7()),
            "name": _to_text(_first(item, "name", "toolName", "tool_name", "function_name")),
            "arguments": _to_json_text(_first(item, "arguments", "functionArguments", "function_arguments")),
            "content": _to_json_text(_first(item, "content", "result")),
        }
        for item in value
        if isinstance(item, dict)
    ]


class ReplyNode(INode):
    serializer_class = ReplyNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = "reply-node"

    def execute(self):
        node_params = self.get_parameters()
        chunk_id = uuid.uuid7()

        reply_type = node_params.get("reply_type")
        fields = node_params.get("fields")
        content = node_params.get("content")
        content_type = node_params.get("content_type") or "TEXT"
        is_result = node_params.get("is_result", False)
        self.data["content_type"] = content_type

        if reply_type == "referencing":
            value = self._get_reference_value(fields)
        else:
            value = self._generate_reply_content(content)

        node_info = NodeInfo(self.get_node_id(), self.get_node_name(), Status.SUCCESS)
        position = Position(self.get_node_id())
        if content_type == "TOOL":
            tool_list = _to_tool_list(value)
            self.write_context("answer", tool_list)
            if is_result:
                for tool in tool_list:
                    self.write(
                        ToolContent(
                            tool["id"],
                            tool["name"],
                            tool["arguments"],
                            tool["content"],
                            Status.SUCCESS,
                            node_info,
                            position,
                        )
                    )
            return

        result = _to_text(value)
        self.write_context("answer", result)
        if is_result:
            content_class = HtmlContent if content_type == "HTML" else TextContent
            self.write(content_class(str(chunk_id), result, Status.SUCCESS, node_info, position))

    def _generate_reply_content(self, prompt):
        if prompt is None:
            return ""
        return self.workflow_manage.generate_prompt(prompt)

    def _get_reference_value(self, fields: List[str]):
        if fields and len(fields) >= 2:
            return self.workflow_manage.get_reference_field(fields[0], fields[1:])
        return ""

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "answer": self.get_context("answer"),
                "content_type": self.data.get("content_type", "TEXT"),
            }
        )
        return details
