# coding=utf-8
import json
import time
from typing import Dict, Optional, Any, Iterator

import requests
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessageChunk, AIMessage
from langchain_core.runnables import RunnableConfig

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class QwenVLChatModel(MaxKBBaseModel, BaseChatOpenAI):

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        chat_tong_yi = QwenVLChatModel(
            model_name=model_name,
            openai_api_key=model_credential.get('api_key'),
            openai_api_base=model_credential.get('api_base') or 'https://dashscope.aliyuncs.com/compatible-mode/v1',
            # stream_options={"include_usage": True},
            streaming=True,
            stream_usage=True,
        )
        return chat_tong_yi

    def check_auth(self, api_key):
        return True
