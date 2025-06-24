from typing import Dict

from openai import OpenAI

from common.config.tokenizer_manage_config import TokenizerManage
from common.utils.common import _remove_empty_lines
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_tts import BaseTextToSpeech


def custom_get_token_ids(text: str):
    tokenizer = TokenizerManage.get_tokenizer()
    return tokenizer.encode(text)


class SiliconCloudTextToSpeech(MaxKBBaseModel, BaseTextToSpeech):
    api_base: str
    api_key: str
    model: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.api_base = kwargs.get('api_base')
        self.model = kwargs.get('model')
        self.params = kwargs.get('params')

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {'voice': 'alloy'}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value
        return SiliconCloudTextToSpeech(
            model=model_name,
            api_base=model_credential.get('api_base'),
            api_key=model_credential.get('api_key'),
            **optional_params,
        )

    def check_auth(self):
        client = OpenAI(
            base_url=self.api_base,
            api_key=self.api_key
        )
        response_list = client.models.with_raw_response.list()
        # print(response_list)

    def text_to_speech(self, text):
        client = OpenAI(
            base_url=self.api_base,
            api_key=self.api_key
        )
        text = _remove_empty_lines(text)
        with client.audio.speech.with_streaming_response.create(
                model=self.model,
                input=text,
                **self.params
        ) as response:
            return response.read()

        import requests

        url = "https://api.siliconflow.cn/v1/audio/speech"

        payload = {
            "model": "FunAudioLLM/CosyVoice2-0.5B",
            "input": "Can you say it with a happy emotion? <|endofprompt|>I'm so happy, Spring Festival is coming!",
            "voice": "FunAudioLLM/CosyVoice2-0.5B:alex",
            "response_format": "mp3",
            "sample_rate": 123,
            "stream": True,
            "speed": 1,
            "gain": 0
        }
        headers = {
            "Authorization": "Bearer <token>",
            "Content-Type": "application/json"
        }

        response = requests.request("POST", url, json=payload, headers=headers)

    def is_cache_model(self):
        return False
