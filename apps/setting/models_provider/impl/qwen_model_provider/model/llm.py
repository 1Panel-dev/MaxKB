# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： llm.py
    @date：2024/4/28 11:44
    @desc:
"""
from typing import Dict

from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class QwenChatModel(MaxKBBaseModel, BaseChatOpenAI):
    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        chat_tong_yi = QwenChatModel(
            model_name=model_name,
            openai_api_key=model_credential.get('api_key'),
            openai_api_base='https://dashscope.aliyuncs.com/compatible-mode/v1',
            streaming=True,
            stream_usage=True,
            extra_body=optional_params
        )
        return chat_tong_yi
