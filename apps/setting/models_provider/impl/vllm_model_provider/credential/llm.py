# coding=utf-8

from typing import Dict

from langchain_core.messages import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class VLLMModelCredential(BaseForm, BaseModelCredential):
    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')
        try:
            model_list = provider.get_base_model_list(model_credential.get('api_base'))
        except Exception as e:
            raise AppApiException(ValidCode.valid_error.value, "API 域名无效")
        exist = provider.get_model_info_by_name(model_list, model_name)
        if len(exist) == 0:
            raise AppApiException(ValidCode.valid_error.value, "模型不存在,请先下载模型")
        model = provider.get_model(model_type, model_name, model_credential)
        try:
            res = model.invoke([HumanMessage(content='你好')])
            print(res)
        except Exception as e:
            print(e)
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

    def get_other_fields(self, model_name):
        return {
            'temperature': {
                'value': 0.7,
                'min': 0.1,
                'max': 1,
                'step': 0.01,
                'label': '温度',
                'precision': 2,
                'tooltip': '较高的数值会使输出更加随机，而较低的数值会使其更加集中和确定'
            },
            'max_tokens': {
                'value': 800,
                'min': 1,
                'max': 4096,
                'step': 1,
                'label': '输出最大Tokens',
                'precision': 0,
                'tooltip': '指定模型可生成的最大token个数'
            }
        }
