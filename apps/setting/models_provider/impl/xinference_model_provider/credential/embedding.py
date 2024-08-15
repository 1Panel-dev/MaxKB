# coding=utf-8
from typing import Dict

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode
from setting.models_provider.impl.local_model_provider.model.embedding import LocalEmbedding


class XinferenceEmbeddingModelCredential(BaseForm, BaseModelCredential):
    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')
        try:
            model_list = provider.get_base_model_list(model_credential.get('api_base'), 'embedding')
        except Exception as e:
            raise AppApiException(ValidCode.valid_error.value, "API 域名无效")
        exist = provider.get_model_info_by_name(model_list, model_name)
        model: LocalEmbedding = provider.get_model(model_type, model_name, model_credential)
        if len(exist) == 0:
            model.start_down_model_thread()
            raise AppApiException(ValidCode.model_not_fount, "模型不存在,请先下载模型")
        model.embed_query('你好')
        return True

    def encryption_dict(self, model_info: Dict[str, object]):
        return model_info

    def build_model(self, model_info: Dict[str, object]):
        for key in ['model']:
            if key not in model_info:
                raise AppApiException(500, f'{key} 字段为必填字段')
        return self

    api_base = forms.TextInputField('API 域名', required=True)
