#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：MaxKB 
@File    ：llm.py
@Author  ：Brian Yang
@Date    ：5/12/24 7:44 AM 
"""
from typing import Dict

from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class DeepSeekChatModel(MaxKBBaseModel, BaseChatOpenAI):

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)

        deepseek_chat_open_ai = DeepSeekChatModel(
            model=model_name,
            openai_api_base='https://api.deepseek.com',
            openai_api_key=model_credential.get('api_key'),
            extra_body=optional_params
        )
        return deepseek_chat_open_ai
