# coding=utf-8
"""
    @project: MaxKB
    @file： text_aggregator.py
    @date：2026/7/22 16:24
    @desc: TextContent 聚合器
"""
from application.workflow.message.aggregator.content_aggregator import ContentAggregator
from application.workflow.message.struct.text_content import TextContent


class TextAggregator(ContentAggregator[TextContent]):
    """
    文本内容聚合器
    用于合并流式文本内容块
    """

    def aggregate(self, prev: TextContent, chunk: TextContent) -> TextContent:
        """
        聚合文本内容
        
        @param prev: 之前的内容
        @param chunk: 新的内容块
        @return: 合并后的内容
        """
        if prev is None:
            return chunk

        # 合并 content
        prev_content = prev.content if prev.content else ""
        chunk_content = chunk.content if chunk.content else ""
        merged_content = prev_content + chunk_content

        # 合并 status: 优先使用 chunk 的，否则使用 prev 的
        merged_status = chunk.status if chunk.status else prev.status

        # 合并基础字段
        merged_id = chunk.id if chunk.id else prev.id
        merged_node_info = chunk.node_info if chunk.node_info else prev.node_info
        merged_position = chunk.position if chunk.position else prev.position

        result = TextContent(merged_id, merged_content, merged_status, merged_node_info, merged_position)

        return result
