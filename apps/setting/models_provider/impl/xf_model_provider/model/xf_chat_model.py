# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： __init__.py.py
    @date：2024/04/19 15:55
    @desc:
"""

from typing import List, Optional, Any, Iterator

from langchain_community.chat_models import ChatSparkLLM
from langchain_community.chat_models.sparkllm import _convert_message_to_dict, _convert_delta_to_message_chunk
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.messages import BaseMessage, AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk


class XFChatSparkLLM(ChatSparkLLM):
    def _stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        default_chunk_class = AIMessageChunk

        self.client.arun(
            [_convert_message_to_dict(m) for m in messages],
            self.spark_user_id,
            self.model_kwargs,
            True,
        )
        for content in self.client.subscribe(timeout=self.request_timeout):
            if "data" not in content:
                continue
            delta = content["data"]
            chunk = _convert_delta_to_message_chunk(delta, default_chunk_class)
            cg_chunk = ChatGenerationChunk(message=chunk)
            if run_manager:
                run_manager.on_llm_new_token(str(chunk.content), chunk=cg_chunk)
            yield cg_chunk
