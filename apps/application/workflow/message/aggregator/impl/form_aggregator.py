"""
@project: MaxKB
@file： form_aggregator.py
@date：2026/9/16
@desc:
"""

from application.workflow.message.aggregator.content_aggregator import ContentAggregator
from application.workflow.message.struct.form_content import FormContent


class FormAggregator(ContentAggregator[FormContent]):
    """
    推理内容聚合器
    用于合并流式推理内容块
    """

    def aggregate(self, prev: FormContent, chunk: FormContent) -> FormContent:
        """
        聚合推理内容

        @param prev: 之前的内容
        @param chunk: 新的内容块
        @return: 合并后的内容
        """
        if prev is None:
            return chunk

        # 合并 status: 优先使用 chunk 的，否则使用 prev 的
        merged_status = chunk.status if chunk.status else prev.status
        form_field_list = chunk.form_field_list if chunk.form_field_list else prev.form_field_list
        form_content_format = chunk.form_content_format if chunk.form_content_format else prev.form_content_format
        is_submit = chunk.is_submit if chunk.is_submit else prev.is_submit
        form_data = chunk.form_data if chunk.form_data else prev.form_data
        # 合并基础字段
        merged_id = chunk.id if chunk.id else prev.id
        merged_node_info = chunk.node_info if chunk.node_info else prev.node_info
        merged_position = chunk.position if chunk.position else prev.position
        result = FormContent(
            merged_id,
            form_field_list,
            form_content_format,
            is_submit,
            merged_status,
            merged_node_info,
            merged_position,
            form_data,
        )
        return result
