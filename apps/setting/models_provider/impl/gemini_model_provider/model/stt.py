from typing import Dict

from django.utils.translation import gettext as _
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_stt import BaseSpeechToText


def custom_get_token_ids(text: str):
    tokenizer = TokenizerManage.get_tokenizer()
    return tokenizer.encode(text)


class GeminiSpeechToText(MaxKBBaseModel, BaseSpeechToText):
    api_key: str
    model: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {}
        if 'max_tokens' in model_kwargs and model_kwargs['max_tokens'] is not None:
            optional_params['max_tokens'] = model_kwargs['max_tokens']
        if 'temperature' in model_kwargs and model_kwargs['temperature'] is not None:
            optional_params['temperature'] = model_kwargs['temperature']
        return GeminiSpeechToText(
            model=model_name,
            api_key=model_credential.get('api_key'),
            **optional_params,
        )

    def check_auth(self):
        client = ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=self.api_key
        )
        response_list = client.invoke(_('Hello'))
        # print(response_list)

    def speech_to_text(self, audio_file):
        client = ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=self.api_key
        )
        audio_data = audio_file.read()
        msg = HumanMessage(content=[
            {'type': 'text', 'text': _('convert audio to text')},
            {"type": "media", 'mime_type': 'audio/mp3', "data": audio_data}
        ])
        res = client.invoke([msg])
        return res.content
