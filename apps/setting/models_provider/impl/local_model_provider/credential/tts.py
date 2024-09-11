# coding=utf-8

from typing import Dict

from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential


class BrowserTextToSpeechCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], provider,
                 raise_exception=False):
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return model
