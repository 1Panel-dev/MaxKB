# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： qian_fan_chat_model.py
    @date：2023/11/10 17:45
    @desc:
"""
from typing import Optional, List, Any, Iterator, cast

from langchain.callbacks.manager import CallbackManager
from langchain.chat_models.base import BaseChatModel
from langchain.load import dumpd
from langchain.schema import LLMResult
from langchain.schema.language_model import LanguageModelInput
from langchain.schema.messages import BaseMessageChunk, BaseMessage, HumanMessage, AIMessage, get_buffer_string
from langchain.schema.output import ChatGenerationChunk
from langchain.schema.runnable import RunnableConfig
from langchain_community.chat_models import QianfanChatEndpoint

from common.config.tokenizer_manage_config import TokenizerManage


class QianfanChatModel(QianfanChatEndpoint):

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        tokenizer = TokenizerManage.get_tokenizer()
        return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])

    def get_num_tokens(self, text: str) -> int:
        tokenizer = TokenizerManage.get_tokenizer()
        return len(tokenizer.encode(text))
