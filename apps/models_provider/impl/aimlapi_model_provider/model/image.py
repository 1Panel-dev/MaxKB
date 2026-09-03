# coding=utf-8
"""
    @project: MaxKB
    @Author：aimlapi.com
    @file： image.py
    @date：2026/09/03 10:00
    @desc:
"""
from typing import Dict

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.aimlapi_model_provider.const import API_BASE, filter_optional_params, get_default_headers
from models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class AIMLAPIImage(MaxKBBaseModel, BaseChatOpenAI):

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        api_base = model_credential.get('api_base') or API_BASE
        optional_params = filter_optional_params(model_kwargs)
        default_headers = optional_params.pop('default_headers', None)
        return AIMLAPIImage(
            model=model_name,
            openai_api_base=api_base,
            openai_api_key=model_credential.get('api_key'),
            default_headers=get_default_headers(api_base, default_headers),
            streaming=True,
            stream_usage=True,
            **optional_params,
        )
