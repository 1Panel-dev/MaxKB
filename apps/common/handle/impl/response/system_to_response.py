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
    def to_block_response(self, chat_id, chat_record_id, content, is_end, completion_tokens,
                          prompt_tokens, other_params: dict = None,
                          _status=status.HTTP_200_OK):
        if other_params is None:
            other_params = {}
        return result.success({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                               'content': content, 'is_end': is_end, **other_params,
                               'completion_tokens': completion_tokens, 'prompt_tokens': prompt_tokens},
                              response_status=_status,
                              code=_status)

    def to_stream_chunk_response(self, chat_id, chat_record_id, node_id, up_node_id_list, content, is_end,
                                 completion_tokens,
                                 prompt_tokens, other_params: dict = None):
        if other_params is None:
            other_params = {}
        chunk = json.dumps({'chat_id': str(chat_id), 'chat_record_id': str(chat_record_id), 'operate': True,
                            'content': content, 'node_id': node_id, 'up_node_id_list': up_node_id_list,
                            'is_end': is_end,
                            'usage': {'completion_tokens': completion_tokens,
                                      'prompt_tokens': prompt_tokens,
                                      'total_tokens': completion_tokens + prompt_tokens},
                            **other_params})
        return super().format_stream_chunk(chunk)
