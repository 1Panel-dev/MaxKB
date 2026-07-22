# coding=utf-8
"""
    @project: MaxKB
    @file： aggregator_factory.py
    @date：2026/7/22 16:24
    @desc: 聚合器工厂
"""
from typing import Dict, Type, Optional

from application.workflow.message.struct.content import Content
from application.workflow.message.struct.text_content import TextContent
from application.workflow.message.struct.reasoning_content import ReasoningContent
from application.workflow.message.struct.tool_content import ToolContent
from application.workflow.message.aggregator.content_aggregator import ContentAggregator
from application.workflow.message.aggregator.impl.text_aggregator import TextAggregator
from application.workflow.message.aggregator.impl.reasoning_aggregator import ReasoningAggregator
from application.workflow.message.aggregator.impl.tool_aggregator import ToolAggregator


class AggregatorFactory:
    """
    聚合器工厂
    根据内容类型获取对应的聚合器
    """
    _aggregators: Dict[Type[Content], ContentAggregator] = {
        TextContent: TextAggregator(),
        ReasoningContent: ReasoningAggregator(),
        ToolContent: ToolAggregator(),
    }

    @classmethod
    def get_aggregator(cls, content_class: Type[Content]) -> ContentAggregator:
        """
        获取聚合器
        
        @param content_class: 内容类型
        @return: 聚合器实例
        @raises ValueError: 如果找不到对应的聚合器
        """
        aggregator = cls._aggregators.get(content_class)
        if aggregator is None:
            raise ValueError(f"No aggregator found for class: {content_class.__name__}")
        return aggregator

    @classmethod
    def get_aggregator_optional(cls, content_class: Type[Content]) -> Optional[ContentAggregator]:
        """
        获取聚合器（可选）
        
        @param content_class: 内容类型
        @return: 聚合器实例或None
        """
        return cls._aggregators.get(content_class)
