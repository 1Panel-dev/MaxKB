# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： reasoning_content.py
    @date：2026/6/30 16:07
    @desc:
"""
from application.workflow.content_type import ContentType
from application.workflow.message.struct.content import Content, NodeInfo, Position
from application.workflow.status import Status


class ReasoningContent(Content):
    def __init__(self, _id, content: str, status: Status, node_info: NodeInfo, position: Position, **kwargs):
        self.content = content
        super().__init__(_id, status, ContentType.REASONING, node_info, position, **kwargs)
