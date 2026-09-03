# coding=utf-8
"""
    @project: MaxKB
    @Author：aimlapi.com
    @file： tti.py
    @date：2026/09/03 10:00
    @desc:
"""
from typing import Dict

from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from models_provider.impl.aimlapi_model_provider.const import API_BASE


class AIMLAPITTIModelParams(BaseForm):
    size = forms.SingleSelect(
        TooltipLabel(_('Image size'),
                     _('Different image models accept different values, keep auto to let the model decide')),
        required=True,
        default_value='auto',
        option_list=[
            {'value': 'auto', 'label': 'auto'},
            {'value': '1024x1024', 'label': '1024x1024'},
            {'value': '1024x1536', 'label': '1024x1536'},
            {'value': '1536x1024', 'label': '1536x1024'},
            {'value': '1024x1792', 'label': '1024x1792'},
            {'value': '1792x1024', 'label': '1792x1024'},
        ],
        text_field='label',
        value_field='value'
    )

    quality = forms.SingleSelect(
        TooltipLabel(_('Picture quality'),
                     _('Different image models accept different values, keep auto to let the model decide')),
        required=True,
        default_value='auto',
        option_list=[
            {'value': 'auto', 'label': 'auto'},
            {'value': 'standard', 'label': 'standard'},
            {'value': 'hd', 'label': 'hd'},
            {'value': 'low', 'label': 'low'},
            {'value': 'medium', 'label': 'medium'},
            {'value': 'high', 'label': 'high'},
        ],
        text_field='label',
        value_field='value'
    )

    n = forms.SliderField(
        TooltipLabel(_('Number of pictures'),
                     _('1 as default')),
        required=True, default_value=1,
        _min=1,
        _max=10,
        _step=1,
        precision=0)


class AIMLAPITextToImageModelCredential(BaseForm, BaseModelCredential):
    api_base = forms.TextInputField('API URL', required=True, default_value=API_BASE)
    api_key = forms.PasswordInputField('API Key', required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  gettext('{model_type} Model type is not supported').format(model_type=model_type))

        for key in ['api_base', 'api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, gettext('{key}  is required').format(key=key))
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            model.check_auth()
        except Exception as e:
            maxkb_logger.error(f'Exception: {e}', exc_info=True)
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

    def get_model_params_setting_form(self, model_name):
        return AIMLAPITTIModelParams()
