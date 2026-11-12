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
        # request_timeout / max_retries 是 OpenAI 客户端配置项，不能随 extra_body 发送到接口请求体，
        # 否则千帆 v2 网关可能返回 500 internal_error，且短超时/关闭重试不会真正生效。
        client_params = {}
        for key in ("request_timeout", "max_retries"):
            if optional_params.get(key) is not None:
                client_params[key] = optional_params.pop(key)
        return QianfanChatModel(
            model=model_name,
            openai_api_base=model_credential.get("api_base"),
            openai_api_key=model_credential.get("api_key"),
            **client_params,
            extra_body=optional_params,
        )
