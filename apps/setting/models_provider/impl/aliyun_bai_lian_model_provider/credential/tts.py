# coding=utf-8

from typing import Dict

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class AliyunBaiLianTTSModelGeneralParams(BaseForm):
    voice = forms.SingleSelect(
        TooltipLabel('音色', '中文音色可支持中英文混合场景'),
        required=True, default_value='longxiaochun',
        text_field='value',
        value_field='value',
        option_list=[
            {'text': '龙小淳', 'value': 'longxiaochun'},
            {'text': '龙小夏', 'value': 'longxiaoxia'},
            {'text': '龙小诚', 'value': 'longxiaocheng'},
            {'text': '龙小白', 'value': 'longxiaobai'},
            {'text': '龙老铁', 'value': 'longlaotie'},
            {'text': '龙书', 'value': 'longshu'},
            {'text': '龙硕', 'value': 'longshuo'},
            {'text': '龙婧', 'value': 'longjing'},
            {'text': '龙妙', 'value': 'longmiao'},
            {'text': '龙悦', 'value': 'longyue'},
            {'text': '龙媛', 'value': 'longyuan'},
            {'text': '龙飞', 'value': 'longfei'},
            {'text': '龙杰力豆', 'value': 'longjielidou'},
            {'text': '龙彤', 'value': 'longtong'},
            {'text': '龙祥', 'value': 'longxiang'},
            {'text': 'Stella', 'value': 'loongstella'},
            {'text': 'Bella', 'value': 'loongbella'},
        ])
    speech_rate = forms.SliderField(
        TooltipLabel('语速', '[0.5,2]，默认为1，通常保留一位小数即可'),
        required=True, default_value=1,
        _min=0.5,
        _max=2,
        _step=0.1,
        precision=1)


class AliyunBaiLianTTSModelCredential(BaseForm, BaseModelCredential):
    api_key = forms.PasswordInputField("API Key", required=True)

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
            model.check_auth()
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
        return AliyunBaiLianTTSModelGeneralParams()
