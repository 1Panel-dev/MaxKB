# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： llm.py
    @date：2024/3/6 11:48
    @desc:
"""
from typing import List, Dict
from urllib.parse import urlparse, ParseResult

from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import BaseMessage, get_buffer_string

from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel


def get_base_url(url: str):
    parse = urlparse(url)
    return ParseResult(scheme=parse.scheme, netloc=parse.netloc, path='', params='',
                       query='',
                       fragment='').geturl()


class OllamaChatModel(MaxKBBaseModel, ChatOpenAI):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        api_base = model_credential.get('api_base', '')
        base_url = get_base_url(api_base)
        return OllamaChatModel(model=model_name, openai_api_base=(base_url + '/v1'),
                               openai_api_key=model_credential.get('api_key'))

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        tokenizer = TokenizerManage.get_tokenizer()
        return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])

    def get_num_tokens(self, text: str) -> int:
        tokenizer = TokenizerManage.get_tokenizer()
        return len(tokenizer.encode(text))
