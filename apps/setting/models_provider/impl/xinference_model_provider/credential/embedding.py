# coding=utf-8
from typing import Dict

from django.utils.translation import gettext as _

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode
from setting.models_provider.impl.local_model_provider.model.embedding import LocalEmbedding


class XinferenceEmbeddingModelCredential(BaseForm, BaseModelCredential):
    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  _('{model_type} Model type is not supported').format(model_type=model_type))
        try:
            model_list = provider.get_base_model_list(model_credential.get('api_base'), model_credential.get('api_key'),
                                                      'embedding')
        except Exception as e:
            raise AppApiException(ValidCode.valid_error.value, _('API domain name is invalid'))
        exist = provider.get_model_info_by_name(model_list, model_name)
        model: LocalEmbedding = provider.get_model(model_type, model_name, model_credential)
        if len(exist) == 0:
            model.start_down_model_thread()
            raise AppApiException(ValidCode.model_not_fount,
                                  _('The model does not exist, please download the model first'))
        model.embed_query(_('Hello'))
        return True

    def encryption_dict(self, model_info: Dict[str, object]):
        return model_info

    def build_model(self, model_info: Dict[str, object]):
        for key in ['model']:
            if key not in model_info:
                raise AppApiException(500, _('{key}  is required').format(key=key))
        return self

    api_base = forms.TextInputField('API URL', required=True)
    api_key = forms.PasswordInputField('API Key', required=True)
