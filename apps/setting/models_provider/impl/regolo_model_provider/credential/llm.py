# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： llm.py
    @date：2024/7/11 18:32
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


class RegoloLLMModelParams(BaseForm):
    temperature = forms.SliderField(TooltipLabel(_('Temperature'),
                                                 _('Higher values make the output more random, while lower values make it more focused and deterministic')),
                                    required=True, default_value=0.7,
                                    _min=0.1,
                                    _max=1.0,
                                    _step=0.01,
                                    precision=2)

    max_tokens = forms.SliderField(
        TooltipLabel(_('Output the maximum Tokens'),
                     _('Specify the maximum number of tokens that the model can generate')),
        required=True, default_value=800,
        _min=1,
        _max=100000,
        _step=1,
        precision=0)


class RegoloLLMModelCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  gettext('{model_type} Model type is not supported').format(model_type=model_type))

        for key in ['api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, gettext('{key}  is required').format(key=key))
                else:
                    return False
        try:

            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            model.invoke([HumanMessage(content=gettext('Hello'))])
        except Exception as e:
            traceback.print_exc()
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value,
                                      gettext(
                                          'Verification failed, please check whether the parameters are correct: {error}').format(
                                          error=str(e)))
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'api_key': super().encryption(model.get('api_key', ''))}

    api_key = forms.PasswordInputField('API Key', required=True)

    def get_model_params_setting_form(self, model_name):
        return RegoloLLMModelParams()
