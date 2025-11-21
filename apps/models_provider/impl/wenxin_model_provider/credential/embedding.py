# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/10/17 15:40
    @desc:
"""
from typing import Dict

from django.utils.translation import gettext as _

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from common.utils.logger import maxkb_logger

class QianfanEmbeddingCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        api_version = model_credential.get('api_version', 'v1')
        model = provider.get_model(model_type, model_name, model_credential, **model_params)
        if api_version == 'v1':
            model_type_list = provider.get_model_type_list()
            if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
                raise AppApiException(ValidCode.valid_error.value,
                                      _('{model_type} Model type is not supported').format(model_type=model_type))
            model_info = [model.lower() for model in model.client.models()]
            if not model_info.__contains__(model_name.lower()):
                raise AppApiException(ValidCode.valid_error.value,
                                      _('{model_name} The model does not support').format(model_name=model_name))
        required_keys = ['qianfan_ak', 'qianfan_sk']
        if api_version == 'v2':
            required_keys = ['api_base', 'qianfan_ak']

        for key in required_keys:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, _('{key}  is required').format(key=key))
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential)
            model.embed_query(_('Hello'))
        except Exception as e:
            maxkb_logger.error(f'Exception: {e}', exc_info=True)
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
        api_version = model.get('api_version', 'v1')
        if api_version == 'v1':
            return {**model, 'qianfan_sk': super().encryption(model.get('qianfan_sk', ''))}
        else:  # v2
            return {**model, 'qianfan_ak': super().encryption(model.get('qianfan_ak', ''))}

    api_version = forms.Radio('API Version', required=True, text_field='label', value_field='value',
                              option_list=[
                                  {'label': 'v1', 'value': 'v1'},
                                  {'label': 'v2', 'value': 'v2'}
                              ],
                              default_value='v1',
                              provider='',
                              method='', )

    # v2版本字段
    api_base = forms.TextInputField("API URL", required=True, relation_show_field_dict={"api_version": ["v2"]})

    # v1版本字段
    qianfan_ak = forms.PasswordInputField('API Key', required=True)
    qianfan_sk = forms.PasswordInputField("Secret Key", required=True,
                                          relation_show_field_dict={"api_version": ["v1"]})
