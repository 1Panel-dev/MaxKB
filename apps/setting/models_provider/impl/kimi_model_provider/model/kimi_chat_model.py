# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： kimi_chat_model.py
    @date：2023/11/10 17:45
    @desc:
"""
from typing import List

from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import BaseMessage, get_buffer_string


class TokenizerManage:
    tokenizer = None

    @staticmethod
    def get_tokenizer():
        from transformers import GPT2TokenizerFast
        if TokenizerManage.tokenizer is None:
            TokenizerManage.tokenizer = GPT2TokenizerFast.from_pretrained('gpt2',
                                                                          cache_dir="/opt/maxkb/model/tokenizer",
                                                                          resume_download=False,
                                                                          force_download=False)
        return TokenizerManage.tokenizer


class KimiChatModel(ChatOpenAI):
    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        tokenizer = TokenizerManage.get_tokenizer()
        return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])

    def get_num_tokens(self, text: str) -> int:
        tokenizer = TokenizerManage.get_tokenizer()
        return len(tokenizer.encode(text))
