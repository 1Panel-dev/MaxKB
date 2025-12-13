# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： llm.py
    @date：2024/7/12 10:19
    @desc:
"""
from typing import Dict

from django.utils.translation import gettext_lazy as _, gettext
from langchain_core.messages import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from common.utils.logger import maxkb_logger

class WenxinLLMModelParams(BaseForm):
    temperature = forms.SliderField(TooltipLabel(_('Temperature'),
                                                 _('Higher values make the output more random, while lower values make it more focused and deterministic')),
                                    required=True, default_value=0.95,
                                    _min=0.1,
                                    _max=1.0,
                                    _step=0.01,
                                    precision=2)

    max_tokens = forms.SliderField(
        TooltipLabel(_('Output the maximum Tokens'),
                     _('Specify the maximum number of tokens that the model can generate')),
        required=True, default_value=1024,
        _min=2,
        _max=100000,
        _step=1,
        precision=0)


class WenxinLLMModelCredential(BaseForm, BaseModelCredential):
    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        # 根据api_version检查必需字段
        api_version = model_credential.get('api_version', 'v1')
        model = provider.get_model(model_type, model_name, model_credential, **model_params)
        if api_version == 'v1':
            model_type_list = provider.get_model_type_list()
            if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
                raise AppApiException(ValidCode.valid_error.value,
                                      gettext('{model_type} Model type is not supported').format(model_type=model_type))
            model_info = [model.lower() for model in model.client.models()]
            if not model_info.__contains__(model_name.lower()):
                raise AppApiException(ValidCode.valid_error.value,
                                      gettext('{model_name} The model does not support').format(model_name=model_name))
        required_keys = ['api_key', 'secret_key']
        if api_version == 'v2':
            required_keys = ['api_base', 'api_key']

        for key in required_keys:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, gettext('{key}  is required').format(key=key))
                else:
                    return False
        try:
            model.invoke(
                [HumanMessage(content=gettext('Hello'))])
        except Exception as e:
            maxkb_logger.error(f'Exception: {e}', exc_info=True)
            raise e
        return True

    def encryption_dict(self, model_info: Dict[str, object]):
        # 根据api_version加密不同字段
        api_version = model_info.get('api_version', 'v1')
        if api_version == 'v1':
            return {**model_info, 'secret_key': super().encryption(model_info.get('secret_key', ''))}
        else:  # v2
            return {**model_info, 'api_key': super().encryption(model_info.get('api_key', ''))}

    def build_model(self, model_info: Dict[str, object]):
        api_version = model_info.get('api_version', 'v1')
        # 根据api_version检查必需字段
        if api_version == 'v1':
            for key in ['api_version', 'api_key', 'secret_key', 'model']:
                if key not in model_info:
                    raise AppApiException(500, gettext('{key}  is required').format(key=key))
            self.api_key = model_info.get('api_key')
            self.secret_key = model_info.get('secret_key')
        else:  # v2
            for key in ['api_version', 'api_base', 'api_key', 'model', ]:
                if key not in model_info:
                    raise AppApiException(500, gettext('{key}  is required').format(key=key))
            self.api_base = model_info.get('api_base')
            self.api_key = model_info.get('api_key')
        return self

    # 动态字段定义 - 根据api_version显示不同字段
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
    api_key = forms.PasswordInputField('API Key', required=True)
    secret_key = forms.PasswordInputField("Secret Key", required=True,
                                          relation_show_field_dict={"api_version": ["v1"]})

    def get_model_params_setting_form(self, model_name):
        return WenxinLLMModelParams()
