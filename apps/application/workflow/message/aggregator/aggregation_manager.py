# coding=utf-8
"""
    @project: MaxKB
    @file： aggregation_manager.py
    @date：2026/7/22 16:24
    @desc: 聚合管理器
"""
from typing import Dict, List

from application.workflow.message.struct.content import Content
from application.workflow.message.aggregator.aggregator_factory import AggregatorFactory


class AggregationManager:
    """
    聚合管理器
    管理内容块的聚合，将相同id和类型的内容合并
    """

    def __init__(self):
        self._key_to_index: Dict[str, int] = {}
        self._contents: List[Content] = []

    @property
    def contents(self) -> List[Content]:
        """获取聚合后的内容列表"""
        return self._contents

    def aggregate(self, chunk: Content) -> None:
        """
        聚合内容块
        
        @param chunk: 内容块
        """
        key = f"{chunk.id}_{chunk.type.value if hasattr(chunk.type, 'value') else chunk.type}"

        idx = self._key_to_index.get(key)
        if idx is None:
            # 新key
            self._key_to_index[key] = len(self._contents)
            self._contents.append(chunk)
        else:
            # 已存在，聚合
            prev = self._contents[idx]
            aggregator = AggregatorFactory.get_aggregator(type(prev))
            self._contents[idx] = aggregator.aggregate(prev, chunk)

    def clear(self) -> None:
        """清空聚合器"""
        self._contents.clear()
        self._key_to_index.clear()

    def get_contents(self) -> List[Dict]:
        """
        获取所有聚合后的内容（字典格式）
        
        @return: 内容字典列表
        """
        return [content.to_dict() for content in self._contents]
