# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： llm.py
    @date：2024/7/11 18:19
    @desc:
"""
from typing import Dict

from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class OllamaLLMModelParams(BaseForm):
    temperature = forms.SliderField(TooltipLabel(_('Temperature'),
                                                 _('Higher values make the output more random, while lower values make it more focused and deterministic')),
                                    required=True, default_value=0.3,
                                    _min=0.1,
                                    _max=1.0,
                                    _step=0.01,
                                    precision=2)

    num_predict = forms.SliderField(
        TooltipLabel(_('Output the maximum Tokens'),
                     _('Specify the maximum number of tokens that the model can generate')),
        required=True, default_value=1024,
        _min=1,
        _max=100000,
        _step=1,
        precision=0)


class OllamaLLMModelCredential(BaseForm, BaseModelCredential):
    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  gettext('{model_type} Model type is not supported').format(model_type=model_type))
        try:
            model_list = provider.get_base_model_list(model_credential.get('api_base'))
        except Exception as e:
            raise AppApiException(ValidCode.valid_error.value, gettext('API domain name is invalid'))
        exist = [model for model in (model_list.get('models') if model_list.get('models') is not None else []) if
                 model.get('model') == model_name or model.get('model').replace(":latest", "") == model_name]
        if len(exist) == 0:
            raise AppApiException(ValidCode.model_not_fount,
                                  gettext('The model does not exist, please download the model first'))
        return True

    def encryption_dict(self, model_info: Dict[str, object]):
        return {**model_info, 'api_key': super().encryption(model_info.get('api_key', ''))}

    def build_model(self, model_info: Dict[str, object]):
        for key in ['api_key', 'model']:
            if key not in model_info:
                raise AppApiException(500, gettext('{key}  is required').format(key=key))
        self.api_key = model_info.get('api_key')
        return self

    api_base = forms.TextInputField('API URL', required=True)
    api_key = forms.PasswordInputField('API Key', required=True)

    def get_model_params_setting_form(self, model_name):
        return OllamaLLMModelParams()
