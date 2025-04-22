# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： llm.py
    @date：2024/7/12 10:19
    @desc:
"""
import traceback
from typing import Dict

from django.utils.translation import gettext_lazy as _, gettext
from langchain_core.messages import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class WenxinLLMModelParams(BaseForm):
    temperature = forms.SliderField(TooltipLabel(_('Temperature'),
                                                 _('Higher values make the output more random, while lower values make it more focused and deterministic')),
                                    required=True, default_value=0.95,
                                    _min=0.1,
                                    _max=1.0,
                                    _step=0.01,
                                    precision=2)

    max_output_tokens = forms.SliderField(
        TooltipLabel(_('Output the maximum Tokens'),
                     _('Specify the maximum number of tokens that the model can generate')),
        required=True, default_value=1024,
        _min=2,
        _max=100000,
        _step=1,
        precision=0)


class WenxinLLMModelCredential(BaseForm, BaseModelCredential):
    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  gettext('{model_type} Model type is not supported').format(model_type=model_type))
        model = provider.get_model(model_type, model_name, model_credential, **model_params)
        model_info = [model.lower() for model in model.client.models()]
        if not model_info.__contains__(model_name.lower()):
            raise AppApiException(ValidCode.valid_error.value,
                                  gettext('{model_name} The model does not support').format(model_name=model_name))
        for key in ['api_key', 'secret_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, gettext('{key}  is required').format(key=key))
                else:
                    return False
        try:
            model.invoke(
                [HumanMessage(content=gettext('Hello'))])
        except Exception as e:
            traceback.print_exc()
            raise e
        return True

    def encryption_dict(self, model_info: Dict[str, object]):
        return {**model_info, 'secret_key': super().encryption(model_info.get('secret_key', ''))}

    def build_model(self, model_info: Dict[str, object]):
        for key in ['api_key', 'secret_key', 'model']:
            if key not in model_info:
                raise AppApiException(500, gettext('{key}  is required').format(key=key))
        self.api_key = model_info.get('api_key')
        self.secret_key = model_info.get('secret_key')
        return self

    api_key = forms.PasswordInputField('API Key', required=True)

    secret_key = forms.PasswordInputField("Secret Key", required=True)

    def get_model_params_setting_form(self, model_name):
        return WenxinLLMModelParams()
