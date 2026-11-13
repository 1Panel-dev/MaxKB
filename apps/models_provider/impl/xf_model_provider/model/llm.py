# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： llm.py
@date：2026/11/13
@desc: Xunfei Spark OpenAI 兼容模型（X2.x 模型走 OpenAI Chat 协议）
"""

from typing import Any, Dict

from langchain_core.language_models import LanguageModelInput
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class XunFeiOpenAIChatModel(MaxKBBaseModel, BaseChatOpenAI):
    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return XunFeiOpenAIChatModel(
            model=model_name,
            openai_api_base=model_credential.get("api_base") or "https://maas-api.cn-huabei-1.xf-yun.com/v2",
            openai_api_key=model_credential.get("api_key"),
            **optional_params,
        )

    def _get_request_payload(
        self,
        input_: LanguageModelInput,
        *,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> dict:
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)
        # 星火 OpenAI 兼容接口使用 max_tokens 字段，而不是 OpenAI 新版的 max_completion_tokens。
        if "max_completion_tokens" in payload and "max_tokens" not in payload:
            payload["max_tokens"] = payload.pop("max_completion_tokens")
        return payload
