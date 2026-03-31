#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：MaxKB 
@File    ：llm.py
@Author  ：Brian Yang
@Date    ：5/12/24 7:44 AM 
"""
import json
from typing import Dict, Any

from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import AIMessage

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class DeepSeekChatModel(MaxKBBaseModel, BaseChatOpenAI):

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)

        deepseek_chat_open_ai = DeepSeekChatModel(
            model=model_name,
            openai_api_base=model_credential.get('api_base') or 'https://api.deepseek.com',
            openai_api_key=model_credential.get('api_key'),
            **optional_params,
        )
        return deepseek_chat_open_ai

    def _get_request_payload(
            self,
            input_: LanguageModelInput,
            *,
            stop: list[str] | None = None,
            **kwargs: Any,
    ) -> dict:
        # Get original messages to preserve reasoning_content before base conversion
        messages = self._convert_input(input_).to_messages()
        # Store reasoning_content for AIMessages with tool_calls
        # According to DeepSeek API docs, reasoning_content is REQUIRED when tool_calls
        # are present during the tool invocation process (within same question/turn).
        # See: https://api-docs.deepseek.com/guides/thinking_mode#tool-calls
        reasoning_content_map = {}
        for i, msg in enumerate(messages):
            if (
                    isinstance(msg, AIMessage)
                    and (msg.tool_calls or msg.invalid_tool_calls)
                    and (reasoning := msg.additional_kwargs.get("reasoning_content"))
            ):
                reasoning_content_map[i] = reasoning

        payload = super()._get_request_payload(input_, stop=stop, **kwargs)

        # Restore reasoning_content for assistant messages with tool_calls
        # This is required by DeepSeek API - missing it causes 400 error
        if "messages" in payload and reasoning_content_map:
            for i, message in enumerate(payload["messages"]):
                if (
                        i in reasoning_content_map
                        and message.get("role") == "assistant"
                        and message.get("tool_calls")
                ):
                    message["reasoning_content"] = reasoning_content_map[i]

        # Apply DeepSeek-specific message formatting
        for message in payload["messages"]:
            if message["role"] == "tool" and isinstance(message["content"], list):
                message["content"] = json.dumps(message["content"])
            elif message["role"] == "assistant" and isinstance(
                    message["content"], list
            ):
                # DeepSeek API expects assistant content to be a string, not a list.
                # Extract text blocks and join them, or use empty string if none exist.
                text_parts = [
                    block.get("text", "")
                    for block in message["content"]
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                message["content"] = "".join(text_parts) if text_parts else ""
        return payload
