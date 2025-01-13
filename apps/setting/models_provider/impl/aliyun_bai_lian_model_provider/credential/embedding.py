# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/10/16 17:01
    @desc:
"""
from typing import Dict

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import ValidCode, BaseModelCredential
from setting.models_provider.impl.aliyun_bai_lian_model_provider.model.embedding import AliyunBaiLianEmbedding
from django.utils.translation import gettext_lazy as _


class AliyunBaiLianEmbeddingCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  _('{model_type} Model type is not supported').format(model_type=model_type))
        for key in ['dashscope_api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, _('{key} is required').format(key=key))
                else:
                    return False
        try:
            model: AliyunBaiLianEmbedding = provider.get_model(model_type, model_name, model_credential)
            model.embed_query(_('Hello'))
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, _('Verification failed, please check whether the parameters are correct: {error}').format(error=str(e)))
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'dashscope_api_key': super().encryption(model.get('dashscope_api_key', ''))}

    dashscope_api_key = forms.PasswordInputField('API Key', required=True)
