# coding=utf-8
import base64
import os
from typing import Dict

from langchain_core.messages import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class OpenAITTIModelParams(BaseForm):
    size = forms.SingleSelect(
        TooltipLabel('图片尺寸', '指定生成图片的尺寸, 如: 1024x1024'),
        required=True,
        default_value='1024x1024',
        option_list=[
            {'value': '1024x1024', 'label': '1024x1024'},
            {'value': '1024x1792', 'label': '1024x1792'},
            {'value': '1792x1024', 'label': '1792x1024'},
        ],
        text_field='label',
        value_field='value'
    )

    quality = forms.SingleSelect(
        TooltipLabel('图片质量', ''),
        required=True,
        default_value='standard',
        option_list=[
            {'value': 'standard', 'label': 'standard'},
            {'value': 'hd', 'label': 'hd'},
        ],
        text_field='label',
        value_field='value'
    )

    n = forms.SliderField(
        TooltipLabel('图片数量', '指定生成图片的数量'),
        required=True, default_value=1,
        _min=1,
        _max=10,
        _step=1,
        precision=0)


class OpenAITextToImageModelCredential(BaseForm, BaseModelCredential):
    api_base = forms.TextInputField('API 域名', required=True)
    api_key = forms.PasswordInputField('API Key', required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')

        for key in ['api_base', 'api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential)
            res = model.check_auth()
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
        return {**model, 'api_key': super().encryption(model.get('api_key', ''))}

    def get_model_params_setting_form(self, model_name):
        return OpenAITTIModelParams()
