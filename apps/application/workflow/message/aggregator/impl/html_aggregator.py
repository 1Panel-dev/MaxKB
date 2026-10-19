# coding=utf-8
"""
@project: MaxKB
@file： html_aggregator.py
@date：2026/10/16
@desc: HtmlContent 聚合器
"""

from application.workflow.message.aggregator.content_aggregator import ContentAggregator
from application.workflow.message.struct.html_content import HtmlContent


class HtmlAggregator(ContentAggregator[HtmlContent]):
    """
    HTML 内容聚合器
    与文本一致,按顺序拼接内容块
    """

    def aggregate(self, prev: HtmlContent, chunk: HtmlContent) -> HtmlContent:
        if prev is None:
            return chunk
        return HtmlContent(
            chunk.id or prev.id,
            (prev.content or "") + (chunk.content or ""),
            chunk.status or prev.status,
            chunk.node_info or prev.node_info,
            chunk.position or prev.position,
        )
