# coding=utf-8
"""
    @project: MaxKB
    @file： content_aggregator.py
    @date：2026/7/22 16:24
    @desc: 内容聚合器接口
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from application.workflow.message.struct.content import Content

T = TypeVar('T', bound=Content)


class ContentAggregator(ABC, Generic[T]):
    """
    内容聚合器接口
    用于合并相同类型的流式内容块
    """

    @abstractmethod
    def aggregate(self, prev: T, chunk: T) -> T:
        """
        聚合两个内容块
        
        @param prev: 之前的内容
        @param chunk: 新的内容块
        @return: 合并后的内容
        """
        pass

    def merge_base_fields(self, prev: T, chunk: T, result: T) -> None:
        """
        合并基础字段
        
        @param prev: 之前的内容
        @param chunk: 新的内容块
        @param result: 结果对象
        """
        result.id = chunk.id if chunk.id else prev.id
        result.status = chunk.status if chunk.status else prev.status
        result.node_info = chunk.node_info if chunk.node_info else prev.node_info
        result.position = chunk.position if chunk.position else prev.position
        result.extra = chunk.extra if chunk.extra else prev.extra
