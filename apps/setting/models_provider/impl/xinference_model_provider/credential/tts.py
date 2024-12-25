# coding=utf-8
from typing import Dict

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class XInferenceTTSModelGeneralParams(BaseForm):
    # ['中文女', '中文男', '日语男', '粤语女', '英文女', '英文男', '韩语女']
    voice = forms.SingleSelect(
        TooltipLabel('音色', ''),
        required=True, default_value='中文女',
        text_field='value',
        value_field='value',
        option_list=[
            {'text': '中文女', 'value': '中文女'},
            {'text': '中文男', 'value': '中文男'},
            {'text': '日语男', 'value': '日语男'},
            {'text': '粤语女', 'value': '粤语女'},
            {'text': '英文女', 'value': '英文女'},
            {'text': '英文男', 'value': '英文男'},
            {'text': '韩语女', 'value': '韩语女'},
        ])


class XInferenceTTSModelCredential(BaseForm, BaseModelCredential):
    api_base = forms.TextInputField('API 域名', required=True)
    api_key = forms.PasswordInputField('API Key', required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')

        for key in ['api_base', 'api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            model.check_auth()
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
        return XInferenceTTSModelGeneralParams()
