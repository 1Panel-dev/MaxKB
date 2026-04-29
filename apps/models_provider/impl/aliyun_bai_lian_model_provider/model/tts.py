from typing import Dict

import dashscope

from django.utils.translation import gettext as _

from common.utils.common import _remove_empty_lines
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_tts import BaseTextToSpeech


class AliyunBaiLianTextToSpeech(MaxKBBaseModel, BaseTextToSpeech):
    api_key: str
    base_url: str
    model: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.base_url = kwargs.get('base_url')
        self.model = kwargs.get('model')
        self.params = kwargs.get('params')

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value

        return AliyunBaiLianTextToSpeech(
            model=model_name,
            api_key=model_credential.get('api_key'),
            base_url=model_credential.get('api_base', "https://dashscope.aliyuncs.com/api/v1"),
            **optional_params,
        )

    def check_auth(self):
        self.text_to_speech(_('Hello'))

    def text_to_speech(self, text):
        global audio
        dashscope.api_key = self.api_key
        dashscope.base_http_api_url = self.base_url
        text = _remove_empty_lines(text)
        if 'sambert' in self.model:
            from dashscope.audio.tts import SpeechSynthesizer
            audio = SpeechSynthesizer.call(model=self.model, text=text, **self.params).get_audio_data()
        elif 'qwen' in self.model:
            response = dashscope.MultiModalConversation.call(
                # 如需使用指令控制功能，请将model替换为qwen3-tts-instruct-flash
                model=self.model,
                api_key=self.api_key,
                text=text,
                **self.params
            )
            # 这个的接口返回格式和上面两个不太一样，直接返回了一个url地址，下载后就是音频文件
            audio_url = response.output.audio.url
            res = response.get(audio_url)
            audio = res.content
        elif 'MiniMax' in self.model:
            import requests

            api_url = f"{self.base_url}/services/aigc/multimodal-generation/generation"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "input": {
                    "text": text,
                    **self.params
                }
            }
            response = requests.post(api_url, headers=headers, json=payload)
            audio_hex = response.json().get("output", {}).get("data", {}).get("audio")
            if audio_hex:
                audio = bytes.fromhex(audio_hex)
            else:
                raise Exception('Failed to get audio data from response' + str(response.text))
        else:
            from dashscope.audio.tts_v2 import SpeechSynthesizer
            synthesizer = SpeechSynthesizer(model=self.model, **self.params)
            audio = synthesizer.call(text)
        if audio is None:
            raise Exception('Failed to generate audio')
        if type(audio) == str:
            raise Exception(audio)
        return audio
