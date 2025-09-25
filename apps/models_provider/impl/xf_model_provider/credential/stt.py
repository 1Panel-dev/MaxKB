# coding=utf-8
import traceback
from typing import Dict

from django.utils.translation import gettext as _

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from models_provider.base_model_provider import BaseModelCredential, ValidCode


class XunFeiSTTModelParams(BaseForm):
    language = forms.TextInputField(
        TooltipLabel(_('language'), _('If not passed, the default value is zh_cn')),
        required=True,
        default_value='zh_cn'
    )
    domain = forms.TextInputField(
        TooltipLabel(_('domain'), _('If not passed, the default value is iat')),
        required=True,
        default_value='iat'
    )
    accent = forms.TextInputField(
        TooltipLabel(_('accent'), _('If not passed, the default value is mandarin')),
        required=True,
        default_value='mandarin'
    )


class XunFeiSTTModelCredential(BaseForm, BaseModelCredential):
    spark_api_url = forms.TextInputField('API URL', required=True, default_value='wss://iat-api.xfyun.cn/v2/iat')
    spark_app_id = forms.TextInputField('APP ID', required=True)
    spark_api_key = forms.PasswordInputField("API Key", required=True)
    spark_api_secret = forms.PasswordInputField('API Secret', required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  _('{model_type} Model type is not supported').format(model_type=model_type))

        for key in ['spark_api_url', 'spark_app_id', 'spark_api_key', 'spark_api_secret']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, _('{key}  is required').format(key=key))
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            model.check_auth()
        except Exception as e:
            traceback.print_exc()
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value,
                                      _('Verification failed, please check whether the parameters are correct: {error}').format(
                                          error=str(e)))
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'spark_api_secret': super().encryption(model.get('spark_api_secret', ''))}

    def get_model_params_setting_form(self, model_name):
        return XunFeiSTTModelParams()
