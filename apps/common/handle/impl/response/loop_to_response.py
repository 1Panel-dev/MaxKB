# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： LoopToResponse.py
    @date：2025/3/12 17:21
    @desc:
"""
import json

from common.handle.impl.response.system_to_response import SystemToResponse


class LoopToResponse(SystemToResponse):

    def to_stream_chunk_response(self, chat_id, chat_record_id, node_id, up_node_id_list, content, is_end,
                                 completion_tokens,
                                 prompt_tokens, other_params: dict = None):
        if other_params is None:
            other_params = {}
        return {'chat_id': str(chat_id), 'chat_record_id': str(chat_record_id), 'operate': True,
                'content': content, 'node_id': node_id, 'up_node_id_list': up_node_id_list,
                'is_end': is_end,
                'usage': {'completion_tokens': completion_tokens,
                          'prompt_tokens': prompt_tokens,
                          'total_tokens': completion_tokens + prompt_tokens},
                **other_params}
