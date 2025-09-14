import base64
import os
import traceback
from typing import Dict

from openai import OpenAI

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_stt import BaseSpeechToText



class VllmWhisperSpeechToText(MaxKBBaseModel, BaseSpeechToText):
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
        return VllmWhisperSpeechToText(
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

        base_url = self.api_url if self.api_url.endswith('v1') else f"{self.api_url}/v1"

        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url=base_url
            )

            result = client.audio.transcriptions.create(
                file=audio_file,
                model=self.model,
                language=self.params.get('Language'),
                response_format="json"
            )

            return result.text

        except Exception as err:
            maxkb_logger.error(f":Error: {str(err)}: {traceback.format_exc()}")