# coding=utf-8

from typing import Dict

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class XunFeiTTSModelGeneralParams(BaseForm):
    vcn = forms.SingleSelect(
        TooltipLabel('发音人', '发音人，可选值：请到控制台添加试用或购买发音人，添加后即显示发音人参数值'),
        required=True, default_value='xiaoyan',
        text_field='value',
        value_field='value',
        option_list=[
            {'text': '讯飞小燕', 'value': 'xiaoyan'},
            {'text': '讯飞许久', 'value': 'aisjiuxu'},
            {'text': '讯飞小萍', 'value': 'aisxping'},
            {'text': '讯飞小婧', 'value': 'aisjinger'},
            {'text': '讯飞许小宝', 'value': 'aisbabyxu'},
        ])
    speed = forms.SliderField(
        TooltipLabel('语速', '语速，可选值：[0-100]，默认为50'),
        required=True, default_value=50,
        _min=1,
        _max=100,
        _step=5,
        precision=1)


class XunFeiTTSModelCredential(BaseForm, BaseModelCredential):
    spark_api_url = forms.TextInputField('API 域名', required=True, default_value='wss://tts-api.xfyun.cn/v2/tts')
    spark_app_id = forms.TextInputField('APP ID', required=True)
    spark_api_key = forms.PasswordInputField("API Key", required=True)
    spark_api_secret = forms.PasswordInputField('API Secret', required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')

        for key in ['spark_api_url', 'spark_app_id', 'spark_api_key', 'spark_api_secret']:
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
        return {**model, 'spark_api_secret': super().encryption(model.get('spark_api_secret', ''))}

    def get_model_params_setting_form(self, model_name):
        return XunFeiTTSModelGeneralParams()
