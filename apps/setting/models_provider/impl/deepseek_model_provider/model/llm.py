#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：MaxKB 
@File    ：llm.py
@Author  ：Brian Yang
@Date    ：5/12/24 7:44 AM 
"""
from typing import List, Dict

from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class DeepSeekChatModel(MaxKBBaseModel, BaseChatOpenAI):

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

        deepseek_chat_open_ai = DeepSeekChatModel(
            model=model_name,
            openai_api_base='https://api.deepseek.com',
            openai_api_key=model_credential.get('api_key'),
            **optional_params
        )
        return deepseek_chat_open_ai

