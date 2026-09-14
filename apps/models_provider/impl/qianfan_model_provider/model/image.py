# coding=utf-8
"""
@project: MaxKB
@file： image.py
@desc: 千帆视觉理解模型（v2 OpenAI 兼容接口 /v2/chat/completions）
"""

from typing import Dict

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class QianfanVisionModel(MaxKBBaseModel, BaseChatOpenAI):
    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return QianfanVisionModel(
            model=model_name,
            openai_api_base=model_credential.get("api_base"),
            openai_api_key=model_credential.get("api_key"),
            extra_body=optional_params,
        )
