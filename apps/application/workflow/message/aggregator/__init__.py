# coding=utf-8
"""
    @project: MaxKB
    @file： __init__.py
    @date：2026/7/22 16:24
    @desc: 内容聚合器模块
"""
from application.workflow.message.aggregator.content_aggregator import ContentAggregator
from application.workflow.message.aggregator.aggregator_factory import AggregatorFactory
from application.workflow.message.aggregator.aggregation_manager import AggregationManager

__all__ = ['ContentAggregator', 'AggregatorFactory', 'AggregationManager']
