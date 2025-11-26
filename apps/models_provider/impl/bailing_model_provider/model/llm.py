#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
    @project: maxkb
    @Author: Su Shi
    @file: llm.py
    @date: 2025/11/25 18:00
    @desc: Bailing Chat Model Implementation
"""
from typing import Dict

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class BailingChatModel(MaxKBBaseModel, BaseChatOpenAI):
    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return BailingChatModel(
            model=model_name,
            openai_api_base=model_credential.get('api_base'),
            openai_api_key=model_credential.get('api_key'),
            streaming=True,
            extra_body=optional_params
        )
