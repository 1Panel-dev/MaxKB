# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： content.py
    @date：2026/6/30 15:38
    @desc:
"""
from enum import Enum
from typing import Optional

from application.workflow.content_type import ContentType
from application.workflow.status import Status


class NodeInfo:
    def __init__(self, _id: str, name: str, status: Status):
        self.id = _id
        self.name = name
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status.value if hasattr(self.status, 'value') else str(self.status),
        }


class Position:
    def __init__(self, _id: str, index: Optional[int] = None, children: Optional['Position'] = None):
        self.id = _id
        self.index = index
        self.children = children

    def to_dict(self):
        return {
            'id': self.id,
            'index': self.index,
            'children': self.children.to_dict() if self.children else None,
        }


class Content:
    def __init__(self, _id, status: Status, _type: ContentType, node_info: NodeInfo, position: Position, **kwargs):
        self.id = _id
        self.status = status
        self.type = _type
        self.node_info = node_info
        self.position = position
        self.extra = kwargs

    def to_dict(self):
        result = {
            'id': self.id,
            'type': self.type.value if hasattr(self.type, 'value') else str(self.type),
            'status': self.status.value if hasattr(self.status, 'value') else str(self.status),
            'node_info': self.node_info.to_dict() if self.node_info else None,
            'position': self.position.to_dict() if self.position else None,
        }
        if self.extra:
            result.update(self.extra)
        return result
