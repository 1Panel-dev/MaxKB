# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： openai_chat_model.py
    @date：2024/4/18 15:28
    @desc:
"""
from typing import List

from langchain_core.messages import BaseMessage, get_buffer_string
from langchain_openai import ChatOpenAI

from common.config.tokenizer_manage_config import TokenizerManage


class OpenAIChatModel(ChatOpenAI):
    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        try:
            return super().get_num_tokens_from_messages(messages)
        except Exception as e:
            tokenizer = TokenizerManage.get_tokenizer()
            return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])

    def get_num_tokens(self, text: str) -> int:
        try:
            return super().get_num_tokens(text)
        except Exception as e:
            tokenizer = TokenizerManage.get_tokenizer()
            return len(tokenizer.encode(text))
