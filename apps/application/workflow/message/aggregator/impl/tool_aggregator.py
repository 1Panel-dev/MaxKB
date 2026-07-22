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

        # 合并 content (tool_name)
        prev_content = prev.content if prev.content else ""
        chunk_content = chunk.content if chunk.content else ""
        merged_content = chunk_content if chunk_content else prev_content

        # 合并 arguments
        prev_arguments = prev.arguments if prev.arguments else ""
        chunk_arguments = chunk.arguments if chunk.arguments else ""
        merged_arguments = prev_arguments + chunk_arguments

        # 合并 result
        prev_result = prev.result if prev.result else ""
        chunk_result = chunk.result if chunk.result else ""
        merged_result = prev_result + chunk_result

        # 合并基础字段
        merged_id = chunk.id if chunk.id else prev.id
        merged_status = chunk.status if chunk.status else prev.status
        merged_node_info = chunk.node_info if chunk.node_info else prev.node_info
        merged_position = chunk.position if chunk.position else prev.position

        result = ToolContent(merged_id, merged_content, merged_arguments, merged_result,
                           merged_status, merged_node_info, merged_position)

        return result
