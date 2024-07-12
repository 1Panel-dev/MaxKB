# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： llm.py
    @date：2023/11/10 17:45
    @desc:
"""
from typing import List, Dict

from langchain.schema.messages import BaseMessage, get_buffer_string
from langchain_community.chat_models import QianfanChatEndpoint

from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel


class QianfanChatModel(MaxKBBaseModel, QianfanChatEndpoint):

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return QianfanChatModel(model=model_name,
                                qianfan_ak=model_credential.get('api_key'),
                                qianfan_sk=model_credential.get('secret_key'),
                                streaming=model_kwargs.get('streaming', False))

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        tokenizer = TokenizerManage.get_tokenizer()
        return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])

    def get_num_tokens(self, text: str) -> int:
        tokenizer = TokenizerManage.get_tokenizer()
        return len(tokenizer.encode(text))
