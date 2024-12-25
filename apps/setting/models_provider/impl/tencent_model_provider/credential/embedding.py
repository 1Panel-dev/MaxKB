from typing import Dict

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class TencentEmbeddingCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=True) -> bool:
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')
        self.valid_form(model_credential)
        try:
            model = provider.get_model(model_type, model_name, model_credential)
            model.embed_query('你好')
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'校验失败,请检查参数是否正确: {str(e)}')
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]) -> Dict[str, object]:
        encrypted_secret_key = super().encryption(model.get('SecretKey', ''))
        return {**model, 'SecretKey': encrypted_secret_key}

    SecretId = forms.PasswordInputField('SecretId', required=True)
    SecretKey = forms.PasswordInputField('SecretKey', required=True)
