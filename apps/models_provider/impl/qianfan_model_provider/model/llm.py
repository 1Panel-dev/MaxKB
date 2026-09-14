# coding=utf-8
"""
@project: maxkb
@Author：虎
@file： llm.py
@date：2023/11/10 17:45
@desc:
"""

from typing import Dict

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class QianfanChatModel(MaxKBBaseModel, BaseChatOpenAI):
    """千帆 OpenAI 兼容接口（v2）"""

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return QianfanChatModel(
            model=model_name,
            openai_api_base=model_credential.get("api_base"),
            openai_api_key=model_credential.get("api_key"),
            extra_body=optional_params,
        )
