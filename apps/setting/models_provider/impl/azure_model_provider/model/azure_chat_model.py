# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： azure_chat_model.py
    @date：2024/4/28 11:45
    @desc:
"""
from typing import List

from langchain_core.messages import BaseMessage, get_buffer_string
from langchain_openai import AzureChatOpenAI

from common.config.tokenizer_manage_config import TokenizerManage


class AzureChatModel(AzureChatOpenAI):
    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        tokenizer = TokenizerManage.get_tokenizer()
        return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])

    def get_num_tokens(self, text: str) -> int:
        tokenizer = TokenizerManage.get_tokenizer()
        return len(tokenizer.encode(text))
