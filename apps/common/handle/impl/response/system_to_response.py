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
from common.result import result


class SystemToResponse(BaseToResponse):
    def to_stream(self, chat_id, chat_record_id, block: dict):
        # 沿用前端在解析的信封 shape：{chat_id, chat_record_id, content:[block]}
        # 系统格式所有块类型都原样下发（block 即 content.to_dict()）
        return json.dumps(
            {
                "chat_id": str(chat_id),
                "chat_record_id": str(chat_record_id),
                "content": [block],
            },
            ensure_ascii=False,
        )

    def to_stream_end(self, chat_id, chat_record_id, usage: dict = None):
        # 系统格式以 [DONE] 收尾，无需单独结束帧
        return None

    def to_block(self, chat_id, chat_record_id, contents: list, usage: dict = None, _status=status.HTTP_200_OK):
        usage = usage or {}
        answer = "".join(c.get("content", "") for c in (contents or []) if c.get("type") == "TEXT")
        return result.success(
            {
                "chat_id": str(chat_id),
                "id": str(chat_record_id),
                "operate": True,
                "content": answer,
                "is_end": True,
                "completion_tokens": usage.get("completion_tokens", 0),
                "prompt_tokens": usage.get("prompt_tokens", 0),
            },
            response_status=_status,
            code=_status,
        )
