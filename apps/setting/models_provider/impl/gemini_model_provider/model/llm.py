#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：MaxKB 
@File    ：llm.py
@Author  ：Brian Yang
@Date    ：5/13/24 7:40 AM 
"""
from typing import List, Dict

from langchain_core.messages import BaseMessage, get_buffer_string
from langchain_google_genai import ChatGoogleGenerativeAI

from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel


class GeminiChatModel(MaxKBBaseModel, ChatGoogleGenerativeAI):

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {}
        if 'temperature' in model_kwargs:
            optional_params['temperature'] = model_kwargs['temperature']
        if 'max_tokens' in model_kwargs:
            optional_params['max_output_tokens'] = model_kwargs['max_tokens']

        gemini_chat = GeminiChatModel(
            model=model_name,
            google_api_key=model_credential.get('api_key'),
            **optional_params
        )
        return gemini_chat

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        tokenizer = TokenizerManage.get_tokenizer()
        return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])

    def get_num_tokens(self, text: str) -> int:
        tokenizer = TokenizerManage.get_tokenizer()
        return len(tokenizer.encode(text))
