import os
import tempfile
from typing import Dict

import dashscope
from dashscope.audio.asr import (Recognition)

from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_stt import BaseSpeechToText


class AliyunBaiLianSpeechToText(MaxKBBaseModel, BaseSpeechToText):
    api_key: str
    model: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.model = kwargs.get('model')

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {}
        if 'max_tokens' in model_kwargs and model_kwargs['max_tokens'] is not None:
            optional_params['max_tokens'] = model_kwargs['max_tokens']
        if 'temperature' in model_kwargs and model_kwargs['temperature'] is not None:
            optional_params['temperature'] = model_kwargs['temperature']
        return AliyunBaiLianSpeechToText(
            model=model_name,
            api_key=model_credential.get('api_key'),
            **optional_params,
        )

    def check_auth(self):
        cwd = os.path.dirname(os.path.abspath(__file__))
        with open(f'{cwd}/iat_mp3_16k.mp3', 'rb') as f:
            self.speech_to_text(f)

    def speech_to_text(self, audio_file):
        dashscope.api_key = self.api_key
        recognition = Recognition(model=self.model,
                                  format='mp3',
                                  sample_rate=16000,
                                  callback=None)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # 将上传的文件保存到临时文件中
            temp_file.write(audio_file.read())
            # 获取临时文件的路径
            temp_file_path = temp_file.name

        try:
            # 识别临时文件
            result = recognition.call(temp_file_path)
            text = ''
            if result.status_code == 200:
                for sentence in result.get_sentence():
                    text += sentence['text']
                return text
            else:
                raise Exception('Error: ', result.message)
        finally:
            # 删除临时文件
            os.remove(temp_file_path)
