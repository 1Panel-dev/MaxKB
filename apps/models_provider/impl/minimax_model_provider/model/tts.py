# coding=utf-8
from typing import Dict

import requests

from django.utils.translation import gettext as _

from common.utils.common import _remove_empty_lines
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_tts import BaseTextToSpeech


class MiniMaxTextToSpeech(MaxKBBaseModel, BaseTextToSpeech):
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
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {'voice_id': 'English_Graceful_Lady'}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value
        return MiniMaxTextToSpeech(
            model=model_name,
            api_base=model_credential.get('api_base') or 'https://api.minimaxi.com/v1',
            api_key=model_credential.get('api_key'),
            **optional_params,
        )

    def check_auth(self):
        self.text_to_speech(_('Hello'))

    def text_to_speech(self, text):
        text = _remove_empty_lines(text)
        api_base = self.api_base.rstrip('/')
        url = f'{api_base}/t2a_v2'

        if 'audio_setting' not in self.params:
            self.params['audio_setting'] = {'format': 'mp3', }
        payload = {
            'model': self.model,
            'text': text,
            'stream': False,
            **self.params,
        }

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()

        result = response.json()
        if result.get('base_resp', {}).get('status_code', 0) != 0:
            error_msg = result.get('base_resp', {}).get('status_msg', 'Unknown error')
            raise Exception(f'MiniMax TTS API error: {error_msg}')

        audio_hex = result.get('data', {}).get('audio', '')
        if not audio_hex:
            raise Exception('MiniMax TTS API returned empty audio data')

        return bytes.fromhex(audio_hex)
