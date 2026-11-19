# coding=utf-8
"""
@project: MaxKB
@file： usage_content.py
@desc: 一次模型调用的 token 用量。只用于节点内部的 token 统计，节点不会把它输出给前端。
"""

from typing import Optional

from application.workflow.content_type import ContentType
from application.workflow.message.struct.content import Content, NodeInfo, Position
from application.workflow.status import Status


class UsageContent(Content):
    def __init__(self, _id, usage: Optional[dict], node_info: NodeInfo, position: Position, **kwargs):
        # usage 为 LangChain 的 usage_metadata；为空表示模型调用已开始、尚未拿到用量
        self.usage = dict(usage or {})
        super().__init__(_id, Status.RUNNING, ContentType.USAGE, node_info, position, **kwargs)

    def to_dict(self):
        result = super().to_dict()
        result["usage"] = self.usage
        return result
