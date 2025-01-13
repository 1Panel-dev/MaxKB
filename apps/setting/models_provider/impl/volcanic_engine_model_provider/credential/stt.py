# coding=utf-8

from typing import Dict

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode
from django.utils.translation import gettext_lazy as _


class VolcanicEngineSTTModelCredential(BaseForm, BaseModelCredential):
    volcanic_api_url = forms.TextInputField('API Url', required=True, default_value='wss://openspeech.bytedance.com/api/v2/asr')
    volcanic_app_id = forms.TextInputField('App ID', required=True)
    volcanic_token = forms.PasswordInputField('Access Token', required=True)
    volcanic_cluster = forms.TextInputField('Cluster ID', required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, _('{model_type} Model type is not supported').format(model_type=model_type))

        for key in ['volcanic_api_url', 'volcanic_app_id', 'volcanic_token', 'volcanic_cluster']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, _('{key}  is required').format(key=key))
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential)
            model.check_auth()
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, _('Verification failed, please check whether the parameters are correct: {error}').format(error=str(e)))
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'volcanic_token': super().encryption(model.get('volcanic_token', ''))}

    def get_model_params_setting_form(self, model_name):
        pass
