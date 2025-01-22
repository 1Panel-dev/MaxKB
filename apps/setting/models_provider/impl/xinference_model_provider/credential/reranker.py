# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： reranker.py
    @date：2024/9/10 9:46
    @desc:
"""
from typing import Dict

from django.utils.translation import gettext as _
from langchain_core.documents import Document

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class XInferenceRerankerModelCredential(BaseForm, BaseModelCredential):
    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=True):
        if not model_type == 'RERANKER':
            raise AppApiException(ValidCode.valid_error.value,
                                  _('{model_type} Model type is not supported').format(model_type=model_type))
        for key in ['server_url']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, _('{key}  is required').format(key=key))
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential)
            model.compress_documents([Document(page_content=_('Hello'))], _('Hello'))
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value,
                                      _('Verification failed, please check whether the parameters are correct: {error}').format(
                                          error=str(e)))
            else:
                return False
        return True

    def encryption_dict(self, model_info: Dict[str, object]):
        return model_info

    server_url = forms.TextInputField('API URL', required=True)

    api_key = forms.PasswordInputField('API Key', required=False)
