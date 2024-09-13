# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： reranker.py
    @date：2024/9/10 9:46
    @desc:
"""
from typing import Dict

from langchain_core.documents import Document

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class XInferenceRerankerModelCredential(BaseForm, BaseModelCredential):
    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], provider,
                 raise_exception=True):
        if not model_type == 'RERANKER':
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')
        for key in ['server_url']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential)
            model.compress_documents([Document(page_content='你好')], '你好')
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'校验失败,请检查参数是否正确: {str(e)}')
            else:
                return False
        return True

    def encryption_dict(self, model_info: Dict[str, object]):
        return model_info

    server_url = forms.TextInputField('API 域名', required=True)

    api_key = forms.PasswordInputField('API Key', required=False)
