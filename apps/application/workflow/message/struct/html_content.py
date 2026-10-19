# coding=utf-8
"""
@project: MaxKB
@file： html_content.py
@date：2026/10/16
@desc: HTML 内容,前端净化后渲染
"""

from application.workflow.content_type import ContentType
from application.workflow.message.struct.content import Content, NodeInfo, Position
from application.workflow.status import Status


class HtmlContent(Content):
    def __init__(self, _id, content: str, status: Status, node_info: NodeInfo, position: Position, **kwargs):
        self.content = content
        super().__init__(_id, status, ContentType.HTML, node_info, position, **kwargs)

    def to_dict(self):
        result = super().to_dict()
        result["content"] = self.content
        return result
