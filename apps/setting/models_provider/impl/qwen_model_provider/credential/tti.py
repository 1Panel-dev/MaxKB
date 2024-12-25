# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： llm.py
    @date：2024/7/11 18:41
    @desc:
"""
import base64
import os
from typing import Dict

from langchain_core.messages import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class QwenModelParams(BaseForm):
    size = forms.SingleSelect(
        TooltipLabel('图片尺寸', '指定生成图片的尺寸, 如: 1024x1024'),
        required=True,
        default_value='1024*1024',
        option_list=[
            {'value': '1024*1024', 'label': '1024*1024'},
            {'value': '720*1280', 'label': '720*1280'},
            {'value': '768*1152', 'label': '768*1152'},
            {'value': '1280*720', 'label': '1280*720'},
        ],
        text_field='label',
        value_field='value')
    n = forms.SliderField(
        TooltipLabel('图片数量', '指定生成图片的数量'),
        required=True, default_value=1,
        _min=1,
        _max=4,
        _step=1,
        precision=0)
    style = forms.SingleSelect(
        TooltipLabel('风格', '指定生成图片的风格'),
        required=True,
        default_value='<auto>',
        option_list=[
            {'value': '<auto>', 'label': '默认值，由模型随机输出图像风格'},
            {'value': '<photography>', 'label': '摄影'},
            {'value': '<portrait>', 'label': '人像写真'},
            {'value': '<3d cartoon>', 'label': '3D卡通'},
            {'value': '<anime>', 'label': '动画'},
            {'value': '<oil painting>', 'label': '油画'},
            {'value': '<watercolor>', 'label': '水彩'},
            {'value': '<sketch>', 'label': '素描'},
            {'value': '<chinese painting>', 'label': '中国画'},
            {'value': '<flat illustration>', 'label': '扁平插画'},
        ],
        text_field='label',
        value_field='value'
    )


class QwenTextToImageModelCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')
        for key in ['api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
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

    api_key = forms.PasswordInputField('API Key', required=True)

    def get_model_params_setting_form(self, model_name):
        return QwenModelParams()
