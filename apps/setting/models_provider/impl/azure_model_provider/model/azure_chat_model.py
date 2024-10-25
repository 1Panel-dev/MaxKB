# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： azure_chat_model.py
    @date：2024/4/28 11:45
    @desc:
"""

from typing import List, Dict, Optional, Any, Iterator, Type

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.messages import BaseMessage, get_buffer_string, BaseMessageChunk, AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk
from langchain_openai import AzureChatOpenAI
from langchain_openai.chat_models.base import _convert_delta_to_message_chunk

from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel


class AzureChatModel(MaxKBBaseModel, AzureChatOpenAI):
    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)

        return AzureChatModel(
            azure_endpoint=model_credential.get('api_base'),
            openai_api_version=model_credential.get('api_version', '2024-02-15-preview'),
            deployment_name=model_credential.get('deployment_name'),
            openai_api_key=model_credential.get('api_key'),
            openai_api_type="azure",
            **optional_params,
            streaming=True,
        )

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        try:
            return super().get_num_tokens_from_messages(messages)
        except Exception as e:
            tokenizer = TokenizerManage.get_tokenizer()
            return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])

    def get_num_tokens(self, text: str) -> int:
        try:
            return super().get_num_tokens(text)
        except Exception as e:
            tokenizer = TokenizerManage.get_tokenizer()
            return len(tokenizer.encode(text))
