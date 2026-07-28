# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： failure_content.py
    @date：2026/7/27 11:14
    @desc:
"""
from typing import Optional

from application.workflow.content_type import ContentType
from application.workflow.message.struct.content import Content, NodeInfo, Position
from application.workflow.status import Status


class FailureContent(Content):
    def __init__(self, _id, content: str, status: Status, node_info: Optional[NodeInfo], position: Optional[Position],
                 **kwargs):
        self.content = content
        super().__init__(_id, status, ContentType.FAILURE, node_info, position, **kwargs)

    def to_dict(self):
        result = super().to_dict()
        result['content'] = self.content
        return result
