# coding=utf-8
"""
讯飞 TTS 工厂类 Credential，根据 api_version 路由到具体 Credential
"""
from typing import Dict

from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from common.utils.logger import maxkb_logger


class XunFeiDefaultTTSModelCredential(BaseForm, BaseModelCredential):
    """讯飞 TTS 工厂类 Credential，根据 api_version 参数路由到具体实现"""

    api_version = forms.SingleSelect(
        _("API Version"), required=True,
        text_field='label',
        value_field='value',
        default_value='online',
        option_list=[
            {'label': _('Online TTS'), 'value': 'online'},
            {'label': _('Super Humanoid TTS'), 'value': 'super_humanoid'}
        ])

    spark_api_url = forms.TextInputField(_('API URL'), required=True)
    spark_app_id = forms.TextInputField('APP ID', required=True)
    spark_api_key = forms.PasswordInputField("API Key", required=True)
    spark_api_secret = forms.PasswordInputField('API Secret', required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  gettext('{model_type} Model type is not supported').format(model_type=model_type))

        api_version = model_credential.get('api_version', 'online')

        for key in ['spark_api_url', 'spark_app_id', 'spark_api_key', 'spark_api_secret']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, gettext('{key} is required').format(key=key))
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
        return {**model, 'spark_api_secret': super().encryption(model.get('spark_api_secret', ''))}

    def get_model_params_setting_form(self, model_name):
        # params 只包含通用参数，vcn 已在 credential 中
        return XunFeiDefaultTTSModelParams()


class XunFeiDefaultTTSModelParams(BaseForm):
    """工厂类的参数表单，只包含通用参数"""

    speed = forms.SliderField(
        TooltipLabel(_('speaking speed'), _('Speech speed, optional value: [0-100], default is 50')),
        required=True, default_value=50,
        _min=1,
        _max=100,
        _step=5,
        precision=1)
