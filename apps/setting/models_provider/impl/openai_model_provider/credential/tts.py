# coding=utf-8
from typing import Dict

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode

class OpenAITTSModelGeneralParams(BaseForm):
    # alloy, echo, fable, onyx, nova, shimmer
    voice = forms.SingleSelect(
        TooltipLabel('Voice', '尝试不同的声音（合金、回声、寓言、缟玛瑙、新星和闪光），找到一种适合您所需的音调和听众的声音。当前的语音针对英语进行了优化。'),
        required=True, default_value='alloy',
        text_field='value',
        value_field='value',
        option_list=[
            {'text': 'alloy', 'value': 'alloy'},
            {'text': 'echo', 'value': 'echo'},
            {'text': 'fable', 'value': 'fable'},
            {'text': 'onyx', 'value': 'onyx'},
            {'text': 'nova', 'value': 'nova'},
            {'text': 'shimmer', 'value': 'shimmer'},
        ])


class OpenAITTSModelCredential(BaseForm, BaseModelCredential):
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
        return OpenAITTSModelGeneralParams()
