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
    def to_block_response(self, chat_id, chat_record_id, content, is_end, completion_tokens, prompt_tokens,
                          _status=status.HTTP_200_OK):
        pass

    @abstractmethod
    def to_stream_chunk_response(self, chat_id, chat_record_id, content, is_end, completion_tokens, prompt_tokens):
        pass

    @staticmethod
    def format_stream_chunk(response_str):
        return 'data: ' + response_str + '\n\n'
