# coding=utf-8
from typing import Dict

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class MiniMaxChatModel(MaxKBBaseModel, BaseChatOpenAI):

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        extra_body = optional_params.get('extra_body', {})
        if not isinstance(extra_body, dict):
            extra_body = {}
        if 'reasoning_split' not in extra_body:
            extra_body['reasoning_split'] = True
        optional_params['extra_body'] = extra_body
        return MiniMaxChatModel(
            model=model_name,
            openai_api_base=model_credential.get('api_base') or 'https://api.minimaxi.com/v1',
            openai_api_key=model_credential.get('api_key'),
            **optional_params,
        )
