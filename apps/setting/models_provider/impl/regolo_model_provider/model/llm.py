# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： llm.py
    @date：2024/4/18 15:28
    @desc:
"""
from typing import List, Dict

from langchain_core.messages import BaseMessage, get_buffer_string
from langchain_openai.chat_models import ChatOpenAI

from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_chat_open_ai import BaseChatOpenAI


def custom_get_token_ids(text: str):
    tokenizer = TokenizerManage.get_tokenizer()
    return tokenizer.encode(text)


class RegoloChatModel(MaxKBBaseModel, BaseChatOpenAI):

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return RegoloChatModel(
            model=model_name,
            openai_api_base="https://api.regolo.ai/v1",
            openai_api_key=model_credential.get('api_key'),
            extra_body=optional_params
        )
