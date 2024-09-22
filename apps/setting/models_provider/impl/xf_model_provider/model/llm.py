# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： __init__.py.py
    @date：2024/04/19 15:55
    @desc:
"""
import json
from typing import List, Optional, Any, Iterator, Dict

from langchain_community.chat_models.sparkllm import _convert_message_to_dict, _convert_delta_to_message_chunk, \
    ChatSparkLLM
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.messages import BaseMessage, AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk

from setting.models_provider.base_model_provider import MaxKBBaseModel


class XFChatSparkLLM(MaxKBBaseModel, ChatSparkLLM):
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
        return XFChatSparkLLM(
            spark_app_id=model_credential.get('spark_app_id'),
            spark_api_key=model_credential.get('spark_api_key'),
            spark_api_secret=model_credential.get('spark_api_secret'),
            spark_api_url=model_credential.get('spark_api_url'),
            spark_llm_domain=model_name,
            streaming=model_kwargs.get('streaming', False),
            **optional_params
        )

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
        default_chunk_class = AIMessageChunk

        self.client.arun(
            [_convert_message_to_dict(m) for m in messages],
            self.spark_user_id,
            self.model_kwargs,
            True,
        )
        for content in self.client.subscribe(timeout=self.request_timeout):
            if "data" in content:
                delta = content["data"]
                chunk = _convert_delta_to_message_chunk(delta, default_chunk_class)
                cg_chunk = ChatGenerationChunk(message=chunk)
            elif "usage" in content:
                generation_info = content["usage"]
                self.usage_metadata = generation_info
                continue
            else:
                continue
            if cg_chunk is not None:
                if run_manager:
                    run_manager.on_llm_new_token(str(cg_chunk.message.content), chunk=cg_chunk)
            yield cg_chunk
