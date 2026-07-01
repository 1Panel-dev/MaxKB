# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： text_content.py
    @date：2026/6/30 16:03
    @desc:
"""
from application.workflow.content_type import ContentType
from application.workflow.message.struct.content import Content, NodeInfo
from application.workflow.status import Status


class TextContent(Content):
    def __init__(self, _id, content: str, status: Status, node_info: NodeInfo, **kwargs):
        self.content = content
        super().__init__(_id, status, ContentType.TEXT, node_info, **kwargs)
