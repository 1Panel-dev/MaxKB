# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： llm.py
    @date：2024/4/18 15:28
    @desc:
"""
from typing import List, Dict, Optional, Any

from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage, get_buffer_string
from langchain_core.runnables import RunnableConfig
from langchain_openai.chat_models import ChatOpenAI

from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel


def custom_get_token_ids(text: str):
    tokenizer = TokenizerManage.get_tokenizer()
    return tokenizer.encode(text)


class OpenAIChatModel(MaxKBBaseModel, ChatOpenAI):

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        azure_chat_open_ai = OpenAIChatModel(
            model=model_name,
            openai_api_base=model_credential.get('api_base'),
            openai_api_key=model_credential.get('api_key'),
            **optional_params,
            custom_get_token_ids=custom_get_token_ids
        )
        return azure_chat_open_ai

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
