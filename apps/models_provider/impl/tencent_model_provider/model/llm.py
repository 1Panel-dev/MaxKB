# coding=utf-8

from typing import Dict, List

from langchain_core.messages import BaseMessage, get_buffer_string

from common.config.tokenizer_manage_config import TokenizerManage
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_chat_open_ai import BaseChatOpenAI


def custom_get_token_ids(text: str):
    tokenizer = TokenizerManage.get_tokenizer()
    return tokenizer.encode(text)


class TencentModel(MaxKBBaseModel, BaseChatOpenAI):
    """Tencent TokenHub LLM model.

    TokenHub aggregates Tencent Hunyuan and other providers behind an
    OpenAI Chat Completions compatible API, see
    https://cloud.tencent.com/document/product/1823/132252
    """

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        streaming = model_kwargs.get("streaming", False)
        return TencentModel(
            model=model_name,
            openai_api_base=model_credential.get("api_base"),
            openai_api_key=model_credential.get("api_key"),
            streaming=streaming,
            custom_get_token_ids=custom_get_token_ids,
            **optional_params,
        )

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        try:
            return super().get_num_tokens_from_messages(messages)
        except Exception:
            tokenizer = TokenizerManage.get_tokenizer()
            return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])

    def get_num_tokens(self, text: str) -> int:
        try:
            return super().get_num_tokens(text)
        except Exception:
            tokenizer = TokenizerManage.get_tokenizer()
            return len(tokenizer.encode(text))
