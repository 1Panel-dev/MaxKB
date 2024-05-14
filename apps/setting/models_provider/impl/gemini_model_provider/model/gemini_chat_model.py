#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：MaxKB 
@File    ：gemini_chat_model.py
@Author  ：Brian Yang
@Date    ：5/13/24 7:40 AM 
"""
from typing import List

from langchain_core.messages import BaseMessage, get_buffer_string
from langchain_google_genai import ChatGoogleGenerativeAI

from common.config.tokenizer_manage_config import TokenizerManage


class GeminiChatModel(ChatGoogleGenerativeAI):
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
