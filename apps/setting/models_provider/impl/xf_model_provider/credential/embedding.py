# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/10/17 15:40
    @desc:
"""
import traceback
from typing import Dict

from django.utils.translation import gettext as _

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class XFEmbeddingCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  _('{model_type} Model type is not supported').format(model_type=model_type))
        self.valid_form(model_credential)
        try:
            model = provider.get_model(model_type, model_name, model_credential)
            model.embed_query(_('Hello'))
        except Exception as e:
            traceback.print_exc()
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value,
                                      _('Verification failed, please check whether the parameters are correct: {error}').format(
                                          error=str(e)))
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'spark_api_secret': super().encryption(model.get('spark_api_secret', ''))}

    base_url = forms.TextInputField('API URL', required=True, default_value="https://emb-cn-huabei-1.xf-yun.com/")
    spark_app_id = forms.TextInputField('APP ID', required=True)
    spark_api_key = forms.PasswordInputField("API Key", required=True)
    spark_api_secret = forms.PasswordInputField('API Secret', required=True)
