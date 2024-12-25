# coding=utf-8
from typing import Dict

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class ZhiPuTTIModelParams(BaseForm):
    size = forms.SingleSelect(
        TooltipLabel('图片尺寸',
                     '图片尺寸，仅 cogview-3-plus 支持该参数。可选范围：[1024x1024,768x1344,864x1152,1344x768,1152x864,1440x720,720x1440]，默认是1024x1024。'),
        required=True,
        default_value='1024x1024',
        option_list=[
            {'value': '1024x1024', 'label': '1024x1024'},
            {'value': '768x1344', 'label': '768x1344'},
            {'value': '864x1152', 'label': '864x1152'},
            {'value': '1344x768', 'label': '1344x768'},
            {'value': '1152x864', 'label': '1152x864'},
            {'value': '1440x720', 'label': '1440x720'},
            {'value': '720x1440', 'label': '720x1440'},
        ],
        text_field='label',
        value_field='value')


class ZhiPuTextToImageModelCredential(BaseForm, BaseModelCredential):
    api_key = forms.PasswordInputField('API Key', required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')

        for key in ['api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            res = model.check_auth()
            print(res)
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'校验失败,请检查参数是否正确: {str(e)}')
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'api_key': super().encryption(model.get('api_key', ''))}

    def get_model_params_setting_form(self, model_name):
        return ZhiPuTTIModelParams()
