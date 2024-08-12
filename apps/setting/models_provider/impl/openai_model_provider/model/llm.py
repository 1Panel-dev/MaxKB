# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： llm.py
    @date：2024/4/18 15:28
    @desc:
"""
from typing import List, Dict

from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class OpenAIChatModel(MaxKBBaseModel, BaseChatOpenAI):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        azure_chat_open_ai = OpenAIChatModel(
            model=model_name,
            openai_api_base=model_credential.get('api_base'),
            openai_api_key=model_credential.get('api_key'),
            streaming=model_kwargs.get('streaming', False),
            max_tokens=model_kwargs.get('max_tokens', 5),
            temperature=model_kwargs.get('temperature', 0.5),
        )
        return azure_chat_open_ai
