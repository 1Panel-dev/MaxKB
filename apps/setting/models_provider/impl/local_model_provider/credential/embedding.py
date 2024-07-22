# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/7/11 11:06
    @desc:
"""
from typing import Dict

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode
from setting.models_provider.impl.local_model_provider.model.embedding import LocalEmbedding


class LocalEmbeddingCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], provider,
                 raise_exception=False):
        if not model_type == 'EMBEDDING':
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')
        for key in ['cache_folder']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            model: LocalEmbedding = provider.get_model(model_type, model_name, model_credential)
            model.embed_query('你好')
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'校验失败,请检查参数是否正确: {str(e)}')
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return model

    cache_folder = forms.TextInputField('模型目录', required=True)
