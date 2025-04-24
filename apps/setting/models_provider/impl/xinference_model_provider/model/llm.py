# coding=utf-8

from typing import Dict, List
from urllib.parse import urlparse, ParseResult

from langchain_core.messages import BaseMessage, get_buffer_string

from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_chat_open_ai import BaseChatOpenAI


def get_base_url(url: str):
    parse = urlparse(url)
    result_url = ParseResult(scheme=parse.scheme, netloc=parse.netloc, path=parse.path, params='',
                             query='',
                             fragment='').geturl()
    return result_url[:-1] if result_url.endswith("/") else result_url


class XinferenceChatModel(MaxKBBaseModel, BaseChatOpenAI):

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        api_base = model_credential.get('api_base', '')
        base_url = get_base_url(api_base)
        base_url = base_url if base_url.endswith('/v1') else (base_url + '/v1')
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return XinferenceChatModel(
            model=model_name,
            openai_api_base=base_url,
            openai_api_key=model_credential.get('api_key'),
            extra_body=optional_params
        )

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        if self.usage_metadata is None or self.usage_metadata == {}:
            tokenizer = TokenizerManage.get_tokenizer()
            return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])
        return self.usage_metadata.get('input_tokens', 0)

    def get_num_tokens(self, text: str) -> int:
        if self.usage_metadata is None or self.usage_metadata == {}:
            tokenizer = TokenizerManage.get_tokenizer()
            return len(tokenizer.encode(text))
        return self.get_last_generation_info().get('output_tokens', 0)
