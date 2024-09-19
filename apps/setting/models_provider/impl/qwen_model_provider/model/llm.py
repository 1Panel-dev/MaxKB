# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： llm.py
    @date：2024/4/28 11:44
    @desc:
"""
from typing import List, Dict, Optional, Iterator, Any, cast

from langchain_community.chat_models import ChatTongyi
from langchain_community.llms.tongyi import generate_with_last_element_mark
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage, get_buffer_string
from langchain_core.outputs import ChatGenerationChunk, ChatGeneration
from langchain_core.runnables import RunnableConfig, ensure_config

from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel


class QwenChatModel(MaxKBBaseModel, ChatTongyi):
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
        chat_tong_yi = QwenChatModel(
            model_name=model_name,
            dashscope_api_key=model_credential.get('api_key'),
            model_kwargs=optional_params,
        )
        return chat_tong_yi

    usage_metadata: dict = {}

    def get_last_generation_info(self) -> Optional[Dict[str, Any]]:
        return self.usage_metadata

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        return self.usage_metadata.get('input_tokens', 0)

    def get_num_tokens(self, text: str) -> int:
        return self.usage_metadata.get('output_tokens', 0)

    def _stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        params: Dict[str, Any] = self._invocation_params(
            messages=messages, stop=stop, stream=True, **kwargs
        )

        for stream_resp, is_last_chunk in generate_with_last_element_mark(
                self.stream_completion_with_retry(**params)
        ):
            choice = stream_resp["output"]["choices"][0]
            message = choice["message"]
            if (
                    choice["finish_reason"] == "stop"
                    and message["content"] == ""
            ) or (choice["finish_reason"] == "length"):
                token_usage = stream_resp["usage"]
                self.usage_metadata = token_usage
            if (
                    choice["finish_reason"] == "null"
                    and message["content"] == ""
                    and "tool_calls" not in message
            ):
                continue

            chunk = ChatGenerationChunk(
                **self._chat_generation_from_qwen_resp(
                    stream_resp, is_chunk=True, is_last_chunk=is_last_chunk
                )
            )
            if run_manager:
                run_manager.on_llm_new_token(chunk.text, chunk=chunk)
            yield chunk

    def invoke(
            self,
            input: LanguageModelInput,
            config: Optional[RunnableConfig] = None,
            *,
            stop: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> BaseMessage:
        config = ensure_config(config)
        chat_result = cast(
            ChatGeneration,
            self.generate_prompt(
                [self._convert_input(input)],
                stop=stop,
                callbacks=config.get("callbacks"),
                tags=config.get("tags"),
                metadata=config.get("metadata"),
                run_name=config.get("run_name"),
                run_id=config.pop("run_id", None),
                **kwargs,
            ).generations[0][0],
        ).message
        self.usage_metadata = chat_result.response_metadata['token_usage']
        return chat_result
