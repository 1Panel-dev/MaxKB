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
        # request_timeout / max_retries 是 OpenAI 客户端配置项，不能随 extra_body 发送到接口请求体。
        client_params = {}
        for key in ("request_timeout", "max_retries"):
            if optional_params.get(key) is not None:
                client_params[key] = optional_params.pop(key)
        return QianfanVisionModel(
            model=model_name,
            openai_api_base=model_credential.get("api_base"),
            openai_api_key=model_credential.get("api_key"),
            **client_params,
            extra_body=optional_params,
        )
