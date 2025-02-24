# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/7/12 15:10
    @desc:
"""
from typing import Dict

from django.utils.translation import gettext as _

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode
from setting.models_provider.impl.ollama_model_provider.model.reranker import OllamaReranker
from langchain_core.documents import BaseDocumentCompressor, Document
from django.utils.translation import gettext_lazy as _, gettext


class OllamaReRankModelCredential(BaseForm, BaseModelCredential):
    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        if not model_type == 'RERANKER':
            raise AppApiException(ValidCode.valid_error.value,
                                  gettext('{model_type} Model type is not supported').format(model_type=model_type))
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  _('{model_type} Model type is not supported').format(model_type=model_type))
        try:
            model_list = provider.get_base_model_list(model_credential.get('api_base'))
        except Exception as e:
            raise AppApiException(ValidCode.valid_error.value, _('API domain name is invalid'))
        exist = [model for model in (model_list.get('models') if model_list.get('models') is not None else []) if
                 model.get('model') == model_name or model.get('model').replace(":latest", "") == model_name]
        if len(exist) == 0:
            raise AppApiException(ValidCode.model_not_fount,
                                  _('The model does not exist, please download the model first'))

        try:
            model: OllamaReranker = provider.get_model(model_type, model_name, model_credential)
            model.compress_documents([Document(page_content=gettext('Hello'))], gettext('Hello'))
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value,
                                      gettext(
                                          'Verification failed, please check whether the parameters are correct: {error}').format(
                                          error=str(e)))
            else:
                return False
        return True

    def encryption_dict(self, model_info: Dict[str, object]):
        return model_info

    def build_model(self, model_info: Dict[str, object]):
        for key in ['model']:
            if key not in model_info:
                raise AppApiException(500, _('{key}  is required').format(key=key))
        return self

    api_base = forms.TextInputField('API URL', required=True)
