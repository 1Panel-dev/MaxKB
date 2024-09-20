# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： llm.py
    @date：2024/7/11 18:19
    @desc:
"""
from typing import Dict

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class OllamaLLMModelParams(BaseForm):
    temperature = forms.SliderField(TooltipLabel('温度', '较高的数值会使输出更加随机，而较低的数值会使其更加集中和确定'),
                                    required=True, default_value=0.3,
                                    _min=0.1,
                                    _max=1.0,
                                    _step=0.01,
                                    precision=2)

    max_tokens = forms.SliderField(
        TooltipLabel('输出最大Tokens', '指定模型可生成的最大token个数'),
        required=True, default_value=1024,
        _min=1,
        _max=100000,
        _step=1,
        precision=0)


class OllamaLLMModelCredential(BaseForm, BaseModelCredential):
    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')
        try:
            model_list = provider.get_base_model_list(model_credential.get('api_base'))
        except Exception as e:
            raise AppApiException(ValidCode.valid_error.value, "API 域名无效")
        exist = [model for model in (model_list.get('models') if model_list.get('models') is not None else []) if
                 model.get('model') == model_name or model.get('model').replace(":latest", "") == model_name]
        if len(exist) == 0:
            raise AppApiException(ValidCode.model_not_fount, "模型不存在,请先下载模型")
        return True

    def encryption_dict(self, model_info: Dict[str, object]):
        return {**model_info, 'api_key': super().encryption(model_info.get('api_key', ''))}

    def build_model(self, model_info: Dict[str, object]):
        for key in ['api_key', 'model']:
            if key not in model_info:
                raise AppApiException(500, f'{key} 字段为必填字段')
        self.api_key = model_info.get('api_key')
        return self

    api_base = forms.TextInputField('API 域名', required=True)
    api_key = forms.PasswordInputField('API Key', required=True)

    def get_model_params_setting_form(self, model_name):
        return OllamaLLMModelParams()
