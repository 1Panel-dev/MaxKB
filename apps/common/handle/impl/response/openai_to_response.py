# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： openai_to_response.py
@date：2024/9/6 16:08
@desc:
"""

from django.http import JsonResponse
from django.utils import timezone
from openai.types import CompletionUsage
from openai.types.chat import ChatCompletionChunk, ChatCompletionMessage, ChatCompletion
from openai.types.chat.chat_completion import Choice as BlockChoice
from openai.types.chat.chat_completion_chunk import Choice, ChoiceDelta
from rest_framework import status

from common.handle.base_to_response import BaseToResponse


class OpenaiToResponse(BaseToResponse):
    def __init__(self):
        # per-response 状态：tool_id -> index，逐帧分配，客户端按 index 累加 arguments
        self._tool_index = {}

    def _to_tool_call_delta(self, block: dict) -> dict:
        """把一个 ToolContent 块转成 OpenAI 的 delta.tool_calls 项；靠稳定 id 分帧、不缓冲。"""
        tool_id = block.get("id")
        first = tool_id not in self._tool_index
        if first:
            self._tool_index[tool_id] = len(self._tool_index)
        index = self._tool_index[tool_id]
        function = {"arguments": block.get("arguments") or ""}
        if first:
            function["name"] = block.get("content") or ""  # ToolContent.content = 工具名
        tool_call = {"index": index, "type": "function", "function": function}
        if first:
            tool_call["id"] = tool_id
        # 非标扩展：result（与 reasoning_content/chat_id 一致），标准客户端忽略、自家客户端读
        if block.get("result"):
            tool_call["result"] = block.get("result")
        return tool_call

    def to_stream(self, chat_id, chat_record_id, block: dict):
        block_type = block.get("type")
        delta_kwargs = {"chat_id": chat_id}
        if block_type == "TEXT":
            delta_kwargs["content"] = block.get("content", "")
        elif block_type == "REASONING":
            delta_kwargs["reasoning_content"] = block.get("content", "")
        elif block_type == "TOOL":
            delta_kwargs["tool_calls"] = [self._to_tool_call_delta(block)]
        else:
            # FORM / FAILURE 等：OpenAI 流不表达，跳过
            return None
        # 内容帧：finish_reason=None、usage=None（用量只在结束帧给，符合 OpenAI 规范）
        return ChatCompletionChunk(
            id=str(chat_record_id),
            model="",
            object="chat.completion.chunk",
            created=int(timezone.now().timestamp()),
            choices=[Choice(delta=ChoiceDelta(**delta_kwargs), finish_reason=None, index=0)],
        ).json()

    def to_stream_end(self, chat_id, chat_record_id, usage: dict = None):
        # 结束帧：空 delta + finish_reason=stop + 最终用量
        usage = usage or {}
        completion_tokens = usage.get("completion_tokens", 0)
        prompt_tokens = usage.get("prompt_tokens", 0)
        return ChatCompletionChunk(
            id=str(chat_record_id),
            model="",
            object="chat.completion.chunk",
            created=int(timezone.now().timestamp()),
            choices=[Choice(delta=ChoiceDelta(chat_id=chat_id), finish_reason="stop", index=0)],
            usage=CompletionUsage(
                completion_tokens=completion_tokens,
                prompt_tokens=prompt_tokens,
                total_tokens=completion_tokens + prompt_tokens,
            ),
        ).json()

    def to_block(self, chat_id, chat_record_id, contents: list, usage: dict = None, _status=status.HTTP_200_OK):
        usage = usage or {}
        answer = "".join(c.get("content", "") for c in (contents or []) if c.get("type") == "TEXT")
        tool_calls = []
        for c in contents or []:
            if c.get("type") != "TOOL":
                continue
            tc = {
                "index": len(tool_calls),
                "id": c.get("id"),
                "type": "function",
                "function": {"name": c.get("content") or "", "arguments": c.get("arguments") or ""},
            }
            if c.get("result"):
                tc["result"] = c.get("result")
            tool_calls.append(tc)
        message_kwargs = {"role": "assistant", "content": answer}
        if tool_calls:
            message_kwargs["tool_calls"] = tool_calls
        completion_tokens = usage.get("completion_tokens", 0)
        prompt_tokens = usage.get("prompt_tokens", 0)
        data = ChatCompletion(
            id=str(chat_record_id),
            choices=[
                BlockChoice(
                    finish_reason="stop", index=0, chat_id=chat_id, message=ChatCompletionMessage(**message_kwargs)
                )
            ],
            created=int(timezone.now().timestamp()),
            model="",
            object="chat.completion",
            usage=CompletionUsage(
                completion_tokens=completion_tokens,
                prompt_tokens=prompt_tokens,
                total_tokens=completion_tokens + prompt_tokens,
            ),
        ).dict()
        return JsonResponse(data=data, status=_status)
