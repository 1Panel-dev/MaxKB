# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： llm.py
    @date：2024/7/11 17:57
    @desc:
"""
from typing import Dict

from langchain_core.messages import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class VolcanicEngineLLMModelCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')

        for key in ['access_key_id', 'secret_access_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential)
            res = model.invoke([HumanMessage(content='你好')])
            print(res)
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'校验失败,请检查参数是否正确: {str(e)}')
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'access_key_id': super().encryption(model.get('access_key_id', ''))}

    access_key_id = forms.PasswordInputField('Access Key ID', required=True)
    secret_access_key = forms.PasswordInputField('Secret Access Key', required=True)

    def get_other_fields(self):
        return {
            'temperature': {
                'value': 0.3,
                'min': 0.1,
                'max': 1.0,
                'step': 0.01,
                'label': '温度',
                'precision': 2,
                'tooltip': '较高的数值会使输出更加随机，而较低的数值会使其更加集中和确定'
            },
            'max_tokens': {
                'value': 1024,
                'min': 1,
                'max': 4096,
                'step': 1,
                'label': '输出最大Tokens',
                'precision': 0,
                'tooltip': '指定模型可生成的最大token个数'
            }
        }
