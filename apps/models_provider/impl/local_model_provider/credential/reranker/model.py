# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： model.py
    @date：2025/11/7 14:23
    @desc:
"""
import traceback
from typing import Dict

from langchain_core.documents import Document

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from models_provider.impl.local_model_provider.model.reranker import LocalReranker
from django.utils.translation import gettext_lazy as _, gettext


class LocalRerankerCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        if not model_type == 'RERANKER':
            raise AppApiException(ValidCode.valid_error.value,
                                  gettext('{model_type} Model type is not supported').format(model_type=model_type))
        for key in ['cache_dir']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, gettext('{key}  is required').format(key=key))
                else:
                    return False
        try:
            model: LocalReranker = provider.get_model(model_type, model_name, model_credential)
            model.compress_documents([Document(page_content=gettext('Hello'))], gettext('Hello'))
        except Exception as e:
            traceback.print_exc()
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

    def encryption_dict(self, model: Dict[str, object]):
        return model

    cache_dir = forms.TextInputField(_('Model catalog'), required=True)
