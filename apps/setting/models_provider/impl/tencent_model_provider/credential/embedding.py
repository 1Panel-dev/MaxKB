import json
from typing import Dict

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class TencentEmbeddingCredential(BaseForm, BaseModelCredential):
    @classmethod
    def _validate_model_type(cls, model_type: str, provider) -> bool:
        model_type_list = provider.get_model_type_list()
        if not any(mt.get('value') == model_type for mt in model_type_list):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')
        return True

    @classmethod
    def _validate_credential(cls, model_credential: Dict[str, object]) -> credential.Credential:
        for key in ['SecretId', 'SecretKey']:
            if key not in model_credential:
                raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
        return credential.Credential(model_credential['SecretId'], model_credential['SecretKey'])

    @classmethod
    def _test_credentials(cls, client, model_name: str):
        req = models.GetEmbeddingRequest()
        params = {
            "Model": model_name,
            "Input": "测试"
        }
        req.from_json_string(json.dumps(params))
        try:
            res = client.GetEmbedding(req)
            print(res.to_json_string())
        except Exception as e:
            raise AppApiException(ValidCode.valid_error.value, f'校验失败,请检查参数是否正确: {str(e)}')

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], provider,
                 raise_exception=True) -> bool:
        try:
            self._validate_model_type(model_type, provider)
            cred = self._validate_credential(model_credential)
            httpProfile = HttpProfile(endpoint="hunyuan.tencentcloudapi.com")
            clientProfile = ClientProfile(httpProfile=httpProfile)
            client = hunyuan_client.HunyuanClient(cred, "", clientProfile)
            self._test_credentials(client, model_name)
            return True
        except AppApiException as e:
            if raise_exception:
                raise e
            return False

    def encryption_dict(self, model: Dict[str, object]) -> Dict[str, object]:
        encrypted_secret_key = super().encryption(model.get('SecretKey', ''))
        return {**model, 'SecretKey': encrypted_secret_key}

    SecretId = forms.PasswordInputField('SecretId', required=True)
    SecretKey = forms.PasswordInputField('SecretKey', required=True)
