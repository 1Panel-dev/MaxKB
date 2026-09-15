# coding=utf-8
"""
    @project: MaxKB
    @file: llm.py
    @desc: API Route Chat Model
"""
from typing import Dict

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class ApiRouteChatModel(MaxKBBaseModel, BaseChatOpenAI):

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return ApiRouteChatModel(
            model=model_name,
            openai_api_base=model_credential.get('api_base') or "https://global.api-route.com/v1",
            openai_api_key=model_credential.get('api_key'),
            **optional_params,
        )
