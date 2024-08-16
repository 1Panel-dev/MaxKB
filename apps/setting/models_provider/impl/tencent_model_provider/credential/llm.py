# coding=utf-8
from langchain_core.messages import HumanMessage
from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class TencentLLMModelCredential(BaseForm, BaseModelCredential):
    REQUIRED_FIELDS = ['hunyuan_secret_id', 'hunyuan_secret_key']

    @classmethod
    def _validate_model_type(cls, model_type, provider, raise_exception=False):
        if not any(mt['value'] == model_type for mt in provider.get_model_type_list()):
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')
            return False
        return True

    @classmethod
    def _validate_credential_fields(cls, model_credential, raise_exception=False):
        missing_keys = [key for key in cls.REQUIRED_FIELDS if key not in model_credential]
        if missing_keys:
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'{", ".join(missing_keys)} 字段为必填字段')
            return False
        return True

    def is_valid(self, model_type, model_name, model_credential, provider, raise_exception=False):
        if not (self._validate_model_type(model_type, provider, raise_exception) and
                self._validate_credential_fields(model_credential, raise_exception)):
            return False
        try:
            model = provider.get_model(model_type, model_name, model_credential)
            model.invoke([HumanMessage(content='你好')])
        except Exception as e:
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'校验失败,请检查参数是否正确: {str(e)}')
            return False
        return True

    def encryption_dict(self, model):
        return {**model, 'hunyuan_secret_key': super().encryption(model.get('hunyuan_secret_key', ''))}

    hunyuan_secret_id = forms.PasswordInputField('SecretId', required=True)
    hunyuan_secret_key = forms.PasswordInputField('SecretKey', required=True)

    def get_other_fields(self, model_name):
        return {
            'temperature': {
                'value': 0.5,
                'min': 0.1,
                'max': 2.0,
                'step': 0.01,
                'label': '温度',
                'precision': 2,
                'tooltip': '较高的数值会使输出更加随机，而较低的数值会使其更加集中和确定'
            },
        }
