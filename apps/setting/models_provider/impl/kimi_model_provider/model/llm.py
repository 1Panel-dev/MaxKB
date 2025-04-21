# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： llm.py
    @date：2023/11/10 17:45
    @desc:
"""
from typing import Dict

from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class KimiChatModel(MaxKBBaseModel, BaseChatOpenAI):

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        kimi_chat_open_ai = KimiChatModel(
            openai_api_base=model_credential['api_base'],
            openai_api_key=model_credential['api_key'],
            model_name=model_name,
            extra_body=optional_params,
        )
        return kimi_chat_open_ai
