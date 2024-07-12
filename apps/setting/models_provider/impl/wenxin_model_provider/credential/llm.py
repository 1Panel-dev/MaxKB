# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： llm.py
    @date：2024/7/12 10:19
    @desc:
"""
from typing import Dict

from langchain_core.messages import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class WenxinLLMModelCredential(BaseForm, BaseModelCredential):
    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')
        model = provider.get_model(model_type, model_name, model_credential)
        model_info = [model.lower() for model in model.client.models()]
        if not model_info.__contains__(model_name.lower()):
            raise AppApiException(ValidCode.valid_error.value, f'{model_name} 模型不支持')
        for key in ['api_key', 'secret_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            model.invoke(
                [HumanMessage(content='你好')])
        except Exception as e:
            raise e
        return True

    def encryption_dict(self, model_info: Dict[str, object]):
        return {**model_info, 'secret_key': super().encryption(model_info.get('secret_key', ''))}

    def build_model(self, model_info: Dict[str, object]):
        for key in ['api_key', 'secret_key', 'model']:
            if key not in model_info:
                raise AppApiException(500, f'{key} 字段为必填字段')
        self.api_key = model_info.get('api_key')
        self.secret_key = model_info.get('secret_key')
        return self

    api_key = forms.PasswordInputField('API Key', required=True)

    secret_key = forms.PasswordInputField("Secret Key", required=True)
