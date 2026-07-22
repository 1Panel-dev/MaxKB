# coding=utf-8
"""
    @project: MaxKB
    @file： __init__.py
    @date：2026/7/22 16:24
    @desc: 聚合器实现模块
"""
from application.workflow.message.aggregator.impl.text_aggregator import TextAggregator
from application.workflow.message.aggregator.impl.reasoning_aggregator import ReasoningAggregator
from application.workflow.message.aggregator.impl.tool_aggregator import ToolAggregator

__all__ = ['TextAggregator', 'ReasoningAggregator', 'ToolAggregator']
