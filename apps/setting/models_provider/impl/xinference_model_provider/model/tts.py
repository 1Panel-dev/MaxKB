from typing import Dict

from openai import OpenAI

from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_tts import BaseTextToSpeech


def custom_get_token_ids(text: str):
    tokenizer = TokenizerManage.get_tokenizer()
    return tokenizer.encode(text)


class XInferenceTextToSpeech(MaxKBBaseModel, BaseTextToSpeech):
    api_base: str
    api_key: str
    model: str
    voice: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.api_base = kwargs.get('api_base')
        self.model = kwargs.get('model')
        self.voice = kwargs.get('voice', '中文女')

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'voice': '中文女'}
        if 'voice' in model_kwargs and model_kwargs['voice'] is not None:
            optional_params['voice'] = model_kwargs['voice']
        return XInferenceTextToSpeech(
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
        # ['中文女', '中文男', '日语男', '粤语女', '英文女', '英文男', '韩语女']

        with client.audio.speech.with_streaming_response.create(
                model=self.model,
                voice=self.voice,
                input=text,
        ) as response:
            return response.read()

    def is_cache_model(self):
        return False