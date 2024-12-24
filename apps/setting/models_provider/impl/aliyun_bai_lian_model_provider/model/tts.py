from typing import Dict

import dashscope
from dashscope.audio.tts_v2 import *

from common.util.common import _remove_empty_lines
from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_tts import BaseTextToSpeech


class AliyunBaiLianTextToSpeech(MaxKBBaseModel, BaseTextToSpeech):
    api_key: str
    model: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.model = kwargs.get('model')
        self.params = kwargs.get('params')

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {'voice': 'longxiaochun', 'speech_rate': 1.0}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value

        return AliyunBaiLianTextToSpeech(
            model=model_name,
            api_key=model_credential.get('api_key'),
            **optional_params,
        )

    def check_auth(self):
        self.text_to_speech('你好')

    def text_to_speech(self, text):
        dashscope.api_key = self.api_key
        synthesizer = SpeechSynthesizer(model=self.model, **self.params)
        text = _remove_empty_lines(text)
        audio = synthesizer.call(text)
        if type(audio) == str:
            print(audio)
            raise Exception(audio)
        return audio

    def is_cache_model(self):
        return False
