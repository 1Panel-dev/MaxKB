# coding=utf-8
import traceback
from typing import Dict

from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class XunFeiTTSModelGeneralParams(BaseForm):
    vcn = forms.SingleSelect(
        TooltipLabel(_('Speaker'),
                     _('Speaker, optional value: Please go to the console to add a trial or purchase speaker. After adding, the speaker parameter value will be displayed.')),
        required=True, default_value='xiaoyan',
        text_field='value',
        value_field='value',
        option_list=[
            {'text': _('iFlytek Xiaoyan'), 'value': 'xiaoyan'},
            {'text': _('iFlytek Xujiu'), 'value': 'aisjiuxu'},
            {'text': _('iFlytek Xiaoping'), 'value': 'aisxping'},
            {'text': _('iFlytek Xiaojing'), 'value': 'aisjinger'},
            {'text': _('iFlytek Xuxiaobao'), 'value': 'aisbabyxu'},
        ])
    speed = forms.SliderField(
        TooltipLabel(_('speaking speed'), _('Speech speed, optional value: [0-100], default is 50')),
        required=True, default_value=50,
        _min=1,
        _max=100,
        _step=5,
        precision=1)


class XunFeiTTSModelCredential(BaseForm, BaseModelCredential):
    spark_api_url = forms.TextInputField('API URL', required=True, default_value='wss://tts-api.xfyun.cn/v2/tts')
    spark_app_id = forms.TextInputField('APP ID', required=True)
    spark_api_key = forms.PasswordInputField("API Key", required=True)
    spark_api_secret = forms.PasswordInputField('API Secret', required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  gettext('{model_type} Model type is not supported').format(model_type=model_type))

        for key in ['spark_api_url', 'spark_app_id', 'spark_api_key', 'spark_api_secret']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, gettext('{key}  is required').format(key=key))
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
                                      gettext(
                                          'Verification failed, please check whether the parameters are correct: {error}').format(
                                          error=str(e)))
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'spark_api_secret': super().encryption(model.get('spark_api_secret', ''))}

    def get_model_params_setting_form(self, model_name):
        return XunFeiTTSModelGeneralParams()
