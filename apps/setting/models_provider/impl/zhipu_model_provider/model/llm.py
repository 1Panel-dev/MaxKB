# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： llm.py
    @date：2024/4/28 11:42
    @desc:
"""

from langchain_community.chat_models import ChatZhipuAI
from langchain_community.chat_models.zhipuai import _truncate_params, _get_jwt_token, connect_sse, \
    _convert_delta_to_message_chunk
from setting.models_provider.base_model_provider import MaxKBBaseModel
import json
from collections.abc import Iterator
from typing import Any, Dict, List, Optional

from langchain_core.callbacks import (
    CallbackManagerForLLMRun,
)

from langchain_core.messages import (
    AIMessageChunk,
    BaseMessage
)
from langchain_core.outputs import ChatGenerationChunk


class ZhipuChatModel(MaxKBBaseModel, ChatZhipuAI):
    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {}
        if 'max_tokens' in model_kwargs and model_kwargs['max_tokens'] is not None:
            optional_params['max_tokens'] = model_kwargs['max_tokens']
        if 'temperature' in model_kwargs and model_kwargs['temperature'] is not None:
            optional_params['temperature'] = model_kwargs['temperature']

        zhipuai_chat = ZhipuChatModel(
            api_key=model_credential.get('api_key'),
            model=model_name,
            streaming=model_kwargs.get('streaming', False),
            **optional_params
        )
        return zhipuai_chat

    usage_metadata: dict = {}

    def get_last_generation_info(self) -> Optional[Dict[str, Any]]:
        return self.usage_metadata

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        return self.usage_metadata.get('prompt_tokens', 0)

    def get_num_tokens(self, text: str) -> int:
        return self.usage_metadata.get('completion_tokens', 0)

    def _stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """Stream the chat response in chunks."""
        if self.zhipuai_api_key is None:
            raise ValueError("Did not find zhipuai_api_key.")
        if self.zhipuai_api_base is None:
            raise ValueError("Did not find zhipu_api_base.")
        message_dicts, params = self._create_message_dicts(messages, stop)
        payload = {**params, **kwargs, "messages": message_dicts, "stream": True}
        _truncate_params(payload)
        headers = {
            "Authorization": _get_jwt_token(self.zhipuai_api_key),
            "Accept": "application/json",
        }

        default_chunk_class = AIMessageChunk
        import httpx

        with httpx.Client(headers=headers, timeout=60) as client:
            with connect_sse(
                    client, "POST", self.zhipuai_api_base, json=payload
            ) as event_source:
                for sse in event_source.iter_sse():
                    chunk = json.loads(sse.data)
                    if len(chunk["choices"]) == 0:
                        continue
                    choice = chunk["choices"][0]
                    generation_info = {}
                    if "usage" in chunk:
                        generation_info = chunk["usage"]
                        self.usage_metadata = generation_info
                    chunk = _convert_delta_to_message_chunk(
                        choice["delta"], default_chunk_class
                    )
                    finish_reason = choice.get("finish_reason", None)

                    chunk = ChatGenerationChunk(
                        message=chunk, generation_info=generation_info
                    )
                    yield chunk
                    if run_manager:
                        run_manager.on_llm_new_token(chunk.text, chunk=chunk)
                    if finish_reason is not None:
                        break
