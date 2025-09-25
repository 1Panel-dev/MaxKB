import base64
import os.path
import traceback
from typing import Dict

import dashscope

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_stt import BaseSpeechToText


class AliyunBaiLianAsrSpeechToText(MaxKBBaseModel, BaseSpeechToText):
    api_key: str
    api_url: str
    model: str
    params: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.model = kwargs.get('model')
        self.params = kwargs.get('params')
        self.api_url = kwargs.get('api_url')

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return AliyunBaiLianAsrSpeechToText(
            model=model_name,
            api_key=model_credential.get('api_key'),
            api_url=model_credential.get('api_url'),
            params=model_kwargs,
            **model_kwargs
        )

    def check_auth(self):
        cwd = os.path.dirname(os.path.abspath(__file__))
        with open(f'{cwd}/iat_mp3_16k.mp3', 'rb') as audio_file:
            self.speech_to_text(audio_file)

    def speech_to_text(self, audio_file):
        try:

            base64_audio = base64.b64encode(audio_file.read()).decode("utf-8")

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"audio": f"data:audio/mp3;base64,{base64_audio}"},
                    ]
                }
            ]
            response = dashscope.MultiModalConversation.call(
                api_key=self.api_key,
                model=self.model,
                messages=messages,
                result_format="message",
                **self.params
            )
            if response.status_code == 200:
                text = response["output"]["choices"][0]["message"].content[0]["text"]
                return text
            else:
                raise Exception('Error: ', response.message)

        except Exception as err:
            maxkb_logger.error(f":Error: {str(err)}: {traceback.format_exc()}")
