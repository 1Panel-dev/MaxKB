# coding=utf-8
"""
@project: MaxKB
@file： tool_aggregator.py
@date：2026/7/22 16:24
@desc: ToolContent 聚合器
"""

from application.workflow.message.aggregator.content_aggregator import ContentAggregator
from application.workflow.message.struct.tool_content import ToolContent


class ToolAggregator(ContentAggregator[ToolContent]):
    """
    工具内容聚合器
    用于合并流式工具调用内容块
    """

    def aggregate(self, prev: ToolContent, chunk: ToolContent) -> ToolContent:
        """
        聚合工具内容

        @param prev: 之前的内容
        @param chunk: 新的内容块
        @return: 合并后的内容
        """
        if prev is None:
            return chunk

        # 合并 name (tool_name)：取新回退旧
        prev_name = prev.name if prev.name else ""
        chunk_name = chunk.name if chunk.name else ""
        merged_name = chunk_name if chunk_name else prev_name

        # 合并 arguments：拼接
        prev_arguments = prev.arguments if prev.arguments else ""
        chunk_arguments = chunk.arguments if chunk.arguments else ""
        merged_arguments = prev_arguments + chunk_arguments

        # 合并 content(即 result 结果)：拼接
        prev_content = prev.content if prev.content else ""
        chunk_content = chunk.content if chunk.content else ""
        merged_content = prev_content + chunk_content

        # 合并基础字段
        merged_id = chunk.id if chunk.id else prev.id
        merged_status = chunk.status if chunk.status else prev.status
        merged_node_info = chunk.node_info if chunk.node_info else prev.node_info
        merged_position = chunk.position if chunk.position else prev.position

        # ToolContent(_id, tool_name, arguments, result, status, node_info, position)
        result = ToolContent(
            merged_id, merged_name, merged_arguments, merged_content, merged_status, merged_node_info, merged_position
        )

        return result
