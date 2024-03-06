# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： ollama_chat_model.py
    @date：2024/3/6 11:48
    @desc:
"""
from typing import List

from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import BaseMessage, get_buffer_string
from transformers import GPT2TokenizerFast

tokenizer = GPT2TokenizerFast.from_pretrained('gpt2', cache_dir="/opt/maxkb/model/tokenizer", resume_download=False,
                                              force_download=False)


class OllamaChatModel(ChatOpenAI):
    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])

    def get_num_tokens(self, text: str) -> int:
        return len(tokenizer.encode(text))
