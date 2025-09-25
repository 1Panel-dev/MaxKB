import os
import tempfile
from typing import Dict

import dashscope
from dashscope.audio.asr import (Recognition)
from pydub import AudioSegment

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_stt import BaseSpeechToText


class AliyunBaiLianSpeechToText(MaxKBBaseModel, BaseSpeechToText):
    api_key: str
    model: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.model = kwargs.get('model')
        self.params = kwargs.get('params')


    @staticmethod
    def is_cache_model():
        return False

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
            params=model_kwargs,
            **optional_params,
        )

    def check_auth(self):
        cwd = os.path.dirname(os.path.abspath(__file__))
        with open(f'{cwd}/iat_mp3_16k.mp3', 'rb') as f:
            self.speech_to_text(f)

    def speech_to_text(self, audio_file):
        dashscope.api_key = self.api_key
        recognition_params = {
            'model': self.model,
            'format': 'mp3',
            'sample_rate': 16000,
            'callback': None,
            **self.params
        }
        print(recognition_params)
        recognition = Recognition(**recognition_params)


        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # 将上传的文件保存到临时文件中
            temp_file.write(audio_file.read())
            # 获取临时文件的路径
            temp_file_path = temp_file.name

        try:
            audio = AudioSegment.from_file(temp_file_path)
            if audio.channels != 1:
                audio = audio.set_channels(1)
            audio = audio.set_frame_rate(16000)

            # 将转换后的音频文件保存到临时文件中
            audio.export(temp_file_path, format='mp3')
            # 识别临时文件
            result = recognition.call(temp_file_path)
            text = ''
            if result.status_code == 200:
                result_sentence = result.get_sentence()
                if result_sentence is not None:
                    for sentence in result_sentence:
                        text += sentence['text']
                    return text
            else:
                raise Exception('Error: ', result.message)
        finally:
            # 删除临时文件
            os.remove(temp_file_path)
