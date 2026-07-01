# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： tool_content.py
    @date：2026/6/30 16:17
    @desc:
"""
from application.workflow.content_type import ContentType
from application.workflow.message.struct.content import Content, NodeInfo
from application.workflow.status import Status


class ToolContent(Content):
    def __init__(self, _id, tool_name: str, arguments: str, result: str, status: Status, node_info: NodeInfo, **kwargs):
        self.content = tool_name
        self.arguments = arguments
        self.result = result
        super().__init__(_id, status, ContentType.TOOL, node_info, **kwargs)
