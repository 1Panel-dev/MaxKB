from typing import Dict

from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_tts import BaseTextToSpeech



class BrowserTextToSpeech(MaxKBBaseModel, BaseTextToSpeech):
    model: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = kwargs.get('model')

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {}
        if 'max_tokens' in model_kwargs and model_kwargs['max_tokens'] is not None:
            optional_params['max_tokens'] = model_kwargs['max_tokens']
        if 'temperature' in model_kwargs and model_kwargs['temperature'] is not None:
            optional_params['temperature'] = model_kwargs['temperature']
        return BrowserTextToSpeech(
            model=model_name,
            **optional_params,
        )

    def check_auth(self):
        pass

    def text_to_speech(self, text):
        pass
