from typing import Dict

import dashscope

from django.utils.translation import gettext as _

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
        self.text_to_speech(_('Hello'))

    def text_to_speech(self, text):
        dashscope.api_key = self.api_key
        text = _remove_empty_lines(text)
        if 'sambert' in self.model:
            from dashscope.audio.tts import SpeechSynthesizer
            audio = SpeechSynthesizer.call(model=self.model, text=text, **self.params).get_audio_data()
        else:
            from dashscope.audio.tts_v2 import SpeechSynthesizer
            synthesizer = SpeechSynthesizer(model=self.model, **self.params)
            audio = synthesizer.call(text)
        if audio is None:
            raise Exception('Failed to generate audio')
        if type(audio) == str:
            print(audio)
            raise Exception(audio)
        return audio

    def is_cache_model(self):
        return False
