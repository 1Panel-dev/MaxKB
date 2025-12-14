from typing import Dict

import dashscope
from dashscope.api_entities.dashscope_response import DashScopeAPIResponse

from django.utils.translation import gettext as _

from common.utils.common import _remove_empty_lines
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_tts import BaseTextToSpeech


class AliyunBaiLianTextToSpeech(MaxKBBaseModel, BaseTextToSpeech):
    api_key: str
    api_base: str
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
        optional_params = {'params': {'voice': 'longxiaochun', 'speech_rate': 1.0}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value

        return AliyunBaiLianTextToSpeech(
            model=model_name,
            api_key=model_credential.get('api_key'),
            api_base=model_credential.get('api_base'),
            **optional_params,
        )

    def check_auth(self):
        self.text_to_speech(_('Hello'))

    def text_to_speech(self, text):
        dashscope.api_key = self.api_key
        # 如果提供了api_base，则配置dashscope使用自定义endpoint
        if self.api_base:
            dashscope.base_http_url = self.api_base
        text = _remove_empty_lines(text)

        # 为sambert模型使用特定的API
        if 'sambert' in self.model:
            from dashscope.audio.tts import SpeechSynthesizer
            audio = SpeechSynthesizer.call(model=self.model, text=text, **self.params).get_audio_data()
        # 为cosyvoice-v1模型使用tts_v2 API
        elif self.model in ['cosyvoice-v1']:
            from dashscope.audio.tts_v2 import SpeechSynthesizer
            synthesizer = SpeechSynthesizer(model=self.model, **self.params)
            audio = synthesizer.call(text)
        # 其他模型（包括qwen-tts系列）使用multimodal-generation API
        else:
            import requests
            import json

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            # 设置默认参数
            voice = self.params.get('voice', 'Cherry')
            language_type = self.params.get('language_type', 'Chinese')

            data = {
                'model': self.model,
                'input': {
                    'text': text,
                    'voice': voice,
                    'language_type': language_type
                }
            }

            # 添加其他可能的参数
            for key, value in self.params.items():
                if key not in ['voice', 'language_type']:
                    data['input'][key] = value

            url = f"{self.api_base}/api/v1/services/aigc/multimodal-generation/generation" if self.api_base else "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

            response = requests.post(url, headers=headers, data=json.dumps(data))

            if response.status_code != 200:
                raise Exception(f'Failed to generate audio: {response.text}')

            response_data = response.json()

            # 提取音频数据，根据实际返回格式
            if 'output' in response_data and 'audio' in response_data['output']:
                audio_data = response_data['output']['audio']
                audio_url = audio_data.get('url')

                if audio_url:
                    # 下载音频文件
                    audio_response = requests.get(audio_url)
                    if audio_response.status_code == 200:
                        return audio_response.content
                    else:
                        raise Exception(f'Failed to download audio: {audio_response.text}')
                else:
                    raise Exception(f'No audio URL in response: {response_data}')
            else:
                raise Exception(f'Unexpected response format: {response_data}')

        if audio is None:
            raise Exception('Failed to generate audio')
        if type(audio) == str:
            raise Exception(audio)
        return audio

