# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： azure_chat_model.py
    @date：2024/4/28 11:45
    @desc:
"""

from typing import List, Dict, Optional, Any

from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage, get_buffer_string
from langchain_core.runnables import RunnableConfig
from langchain_openai import AzureChatOpenAI

from common.config.tokenizer_manage_config import TokenizerManage
from models_provider.base_model_provider import MaxKBBaseModel


class AzureChatModel(MaxKBBaseModel, AzureChatOpenAI):
    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)

        return AzureChatModel(
            azure_endpoint=model_credential.get('api_base'),
            model_name=model_name,
            openai_api_version=model_credential.get('api_version', '2024-02-15-preview'),
            deployment_name=model_credential.get('deployment_name'),
            openai_api_key=model_credential.get('api_key'),
            openai_api_type="azure",
            **optional_params,
            streaming=True,
        )

    def get_last_generation_info(self) -> Optional[Dict[str, Any]]:
        return self.__dict__.get('_last_generation_info')

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        try:
            return self.get_last_generation_info().get('input_tokens', 0)
        except Exception as e:
            tokenizer = TokenizerManage.get_tokenizer()
            return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])

    def get_num_tokens(self, text: str) -> int:
        try:
            return self.get_last_generation_info().get('output_tokens', 0)
        except Exception as e:
            tokenizer = TokenizerManage.get_tokenizer()
            return len(tokenizer.encode(text))

    def invoke(
            self,
            input: LanguageModelInput,
            config: Optional[RunnableConfig] = None,
            *,
            stop: Optional[list[str]] = None,
            **kwargs: Any,
    ) -> BaseMessage:
        message = super().invoke(input, config, stop=stop, **kwargs)
        if isinstance(message.content, str):
            return message
        elif isinstance(message.content, list):
            # 构造新的响应消息返回
            content = message.content
            normalized_parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get('type') == 'text':
                        normalized_parts.append(item.get('text', ''))
            message.content = ''.join(normalized_parts)
            self.__dict__.setdefault('_last_generation_info', {}).update(message.usage_metadata)
            return message
