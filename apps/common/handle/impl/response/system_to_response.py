# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： system_to_response.py
    @date：2024/9/6 18:03
    @desc:
"""
import json

from rest_framework import status

from common.handle.base_to_response import BaseToResponse
from common.response import result


class SystemToResponse(BaseToResponse):
    def to_block_response(self, chat_id, chat_record_id, content, is_end, completion_tokens, prompt_tokens,
                          _status=status.HTTP_200_OK):
        return result.success({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                               'content': content, 'is_end': is_end}, response_status=_status, code=_status)

    def to_stream_chunk_response(self, chat_id, chat_record_id, content, is_end, completion_tokens, prompt_tokens):
        chunk = json.dumps({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                            'content': content, 'is_end': is_end})
        return super().format_stream_chunk(chunk)
