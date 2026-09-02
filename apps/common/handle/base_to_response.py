# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： base_to_response.py
@date：2024/9/6 16:04
@desc:
"""

from abc import ABC, abstractmethod

from rest_framework import status


class BaseToResponse(ABC):
    @abstractmethod
    def to_stream(self, chat_id, chat_record_id, block: dict):
        """
        把一个内容块(content.to_dict())格式化成一帧 SSE 的 data 载荷(JSON 字符串)。
        返回 None 表示该块类型在此格式下不表达（消费方跳过）。
        只返回 data 载荷，不含 'data:'/'id:' 帧壳，帧壳由消费方拼。
        """
        pass

    @abstractmethod
    def to_stream_end(self, chat_id, chat_record_id, usage: dict = None):
        """
        流结束帧（如 OpenAI 的空 delta + finish_reason=stop + 最终用量）。
        返回 None 表示该格式无需单独结束帧（如系统格式以 [DONE] 收尾）。
        """
        pass

    @abstractmethod
    def to_block(self, chat_id, chat_record_id, contents: list, usage: dict = None, _status=status.HTTP_200_OK):
        """从聚合后的内容块列表(content.to_dict() 的 list)构造非流式响应。"""
        pass

    @staticmethod
    def format_stream_chunk(response_str):
        return "data: " + response_str + "\n\n"
