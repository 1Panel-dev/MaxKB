#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：MaxKB 
@File    ：llm.py
@Author  ：Brian Yang
@Date    ：5/13/24 7:40 AM 
"""
from typing import List, Dict, Optional, Any

from langchain_core.messages import BaseMessage, get_buffer_string
from langchain_google_genai import ChatGoogleGenerativeAI

from common.config.tokenizer_manage_config import TokenizerManage
from models_provider.base_model_provider import MaxKBBaseModel


class GeminiChatModel(MaxKBBaseModel, ChatGoogleGenerativeAI):

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        base_url = model_credential.get('base_url', "https://generativelanguage.googleapis.com")
        if base_url:
            optional_params.setdefault("model_kwargs", {})
            optional_params["model_kwargs"]["http_options"] = {"base_url": base_url}
        gemini_chat = GeminiChatModel(
            model=model_name,
            api_key=model_credential.get('api_key'),
            **optional_params
        )
        return gemini_chat

    def get_last_generation_info(self) -> Optional[Dict[str, Any]]:
        return self.__dict__.get('_last_generation_info')

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        try:
            return self.get_last_generation_info().get('input_tokens', 0)
        except Exception as e:
            tokenizer = TokenizerManage.get_tokenizer()
            return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])

    def get_num_tokens(self, text: str) -> int:
        try:
            return self.get_last_generation_info().get('output_tokens', 0)
        except Exception as e:
            tokenizer = TokenizerManage.get_tokenizer()
            return len(tokenizer.encode(text))
