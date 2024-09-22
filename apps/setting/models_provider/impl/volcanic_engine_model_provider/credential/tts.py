# coding=utf-8

from typing import Dict

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class VolcanicEngineTTSModelCredential(BaseForm, BaseModelCredential):
    volcanic_api_url = forms.TextInputField('API 域名', required=True, default_value='wss://openspeech.bytedance.com/api/v1/tts/ws_binary')
    volcanic_app_id = forms.TextInputField('App ID', required=True)
    volcanic_token = forms.PasswordInputField('Access Token', required=True)
    volcanic_cluster = forms.TextInputField('Cluster ID', required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')

        for key in ['volcanic_api_url', 'volcanic_app_id', 'volcanic_token', 'volcanic_cluster']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential)
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
        return {**model, 'volcanic_token': super().encryption(model.get('volcanic_token', ''))}

    def get_model_params_setting_form(self, model_name):
        pass
