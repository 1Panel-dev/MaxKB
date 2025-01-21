from typing import Dict

from openai import AzureOpenAI

from common.config.tokenizer_manage_config import TokenizerManage
from common.util.common import _remove_empty_lines
from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_tts import BaseTextToSpeech


def custom_get_token_ids(text: str):
    tokenizer = TokenizerManage.get_tokenizer()
    return tokenizer.encode(text)


class AzureOpenAITextToSpeech(MaxKBBaseModel, BaseTextToSpeech):
    api_base: str
    api_key: str
    api_version: str
    model: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.api_base = kwargs.get('api_base')
        self.api_version = kwargs.get('api_version')
        self.model = kwargs.get('model')
        self.params = kwargs.get('params')

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {'voice': 'alloy'}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value
        return AzureOpenAITextToSpeech(
            model=model_name,
            api_base=model_credential.get('api_base'),
            api_key=model_credential.get('api_key'),
            api_version=model_credential.get('api_version'),
            **optional_params,
        )

    def check_auth(self):
        client = AzureOpenAI(
            azure_endpoint=self.api_base,
            api_key=self.api_key,
            api_version=self.api_version
        )
        response_list = client.models.with_raw_response.list()
        # print(response_list)

    def text_to_speech(self, text):
        client = AzureOpenAI(
            azure_endpoint=self.api_base,
            api_key=self.api_key,
            api_version=self.api_version
        )
        text = _remove_empty_lines(text)
        with client.audio.speech.with_streaming_response.create(
                model=self.model,
                input=text,
                **self.params
        ) as response:
            return response.read()

    def is_cache_model(self):
        return False
