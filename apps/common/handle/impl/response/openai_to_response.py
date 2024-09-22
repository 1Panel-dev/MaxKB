# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： openai_to_response.py
    @date：2024/9/6 16:08
    @desc:
"""
import datetime

from django.http import JsonResponse
from openai.types import CompletionUsage
from openai.types.chat import ChatCompletionChunk, ChatCompletionMessage, ChatCompletion
from openai.types.chat.chat_completion import Choice as BlockChoice
from openai.types.chat.chat_completion_chunk import Choice, ChoiceDelta
from rest_framework import status

from common.handle.base_to_response import BaseToResponse


class OpenaiToResponse(BaseToResponse):
    def to_block_response(self, chat_id, chat_record_id, content, is_end, completion_tokens, prompt_tokens,
                          _status=status.HTTP_200_OK):
        data = ChatCompletion(id=chat_record_id, choices=[
            BlockChoice(finish_reason='stop', index=0, chat_id=chat_id,
                        message=ChatCompletionMessage(role='assistant', content=content))],
                              created=datetime.datetime.now().second, model='', object='chat.completion',
                              usage=CompletionUsage(completion_tokens=completion_tokens,
                                                    prompt_tokens=prompt_tokens,
                                                    total_tokens=completion_tokens + prompt_tokens)
                              ).dict()
        return JsonResponse(data=data, status=_status)

    def to_stream_chunk_response(self, chat_id, chat_record_id, content, is_end, completion_tokens, prompt_tokens):
        chunk = ChatCompletionChunk(id=chat_record_id, model='', object='chat.completion.chunk',
                                    created=datetime.datetime.now().second, choices=[
                Choice(delta=ChoiceDelta(content=content, chat_id=chat_id), finish_reason='stop' if is_end else None,
                       index=0)],
                                    usage=CompletionUsage(completion_tokens=completion_tokens,
                                                          prompt_tokens=prompt_tokens,
                                                          total_tokens=completion_tokens + prompt_tokens)).json()
        return super().format_stream_chunk(chunk)
