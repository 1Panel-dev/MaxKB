#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：MaxKB 
@File    ：llm.py
@Author  ：Brian Yang
@Date    ：5/13/24 7:40 AM 
"""
from typing import List, Dict, Optional, Sequence, Union, Any, Iterator, cast

from google.ai.generativelanguage_v1 import GenerateContentResponse
from google.ai.generativelanguage_v1beta.types import (
    Tool as GoogleTool,
)
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatGenerationChunk
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai._function_utils import _ToolConfigDict, _ToolDict
from langchain_google_genai.chat_models import _chat_with_retry, _response_to_result, \
    _FunctionDeclarationType
from langchain_google_genai._common import (
    SafetySettingDict,
)
from setting.models_provider.base_model_provider import MaxKBBaseModel


class GeminiChatModel(MaxKBBaseModel, ChatGoogleGenerativeAI):

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)

        gemini_chat = GeminiChatModel(
            model=model_name,
            google_api_key=model_credential.get('api_key'),
            **optional_params
        )
        return gemini_chat

    def get_last_generation_info(self) -> Optional[Dict[str, Any]]:
        return self.__dict__.get('_last_generation_info')

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        return self.get_last_generation_info().get('input_tokens', 0)

    def get_num_tokens(self, text: str) -> int:
        return self.get_last_generation_info().get('output_tokens', 0)

    def _stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            *,
            tools: Optional[Sequence[Union[_ToolDict, GoogleTool]]] = None,
            functions: Optional[Sequence[_FunctionDeclarationType]] = None,
            safety_settings: Optional[SafetySettingDict] = None,
            tool_config: Optional[Union[Dict, _ToolConfigDict]] = None,
            generation_config: Optional[Dict[str, Any]] = None,
            **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        request = self._prepare_request(
            messages,
            stop=stop,
            tools=tools,
            functions=functions,
            safety_settings=safety_settings,
            tool_config=tool_config,
            generation_config=generation_config,
        )
        response: GenerateContentResponse = _chat_with_retry(
            request=request,
            generation_method=self.client.stream_generate_content,
            **kwargs,
            metadata=self.default_metadata,
        )
        for chunk in response:
            _chat_result = _response_to_result(chunk, stream=True)
            gen = cast(ChatGenerationChunk, _chat_result.generations[0])
            if gen.message:
                token_usage = gen.message.usage_metadata
                self.__dict__.setdefault('_last_generation_info', {}).update(token_usage)
            if run_manager:
                run_manager.on_llm_new_token(gen.text)
            yield gen
