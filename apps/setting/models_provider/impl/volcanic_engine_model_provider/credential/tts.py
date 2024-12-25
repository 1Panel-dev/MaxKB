# coding=utf-8

from typing import Dict

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class VolcanicEngineTTSModelGeneralParams(BaseForm):
    voice_type = forms.SingleSelect(
        TooltipLabel('音色', '中文音色可支持中英文混合场景'),
        required=True, default_value='BV002_streaming',
        text_field='value',
        value_field='value',
        option_list=[
            {'text': '灿灿 2.0', 'value': 'BV700_V2_streaming'},
            {'text': '炀炀', 'value': 'BV705_streaming'},
            {'text': '擎苍 2.0', 'value': 'BV701_V2_streaming'},
            {'text': '通用女声 2.0', 'value': 'BV001_V2_streaming'},
            {'text': '灿灿', 'value': 'BV700_streaming'},
            {'text': '超自然音色-梓梓2.0', 'value': 'BV406_V2_streaming'},
            {'text': '超自然音色-梓梓', 'value': 'BV406_streaming'},
            {'text': '超自然音色-燃燃2.0', 'value': 'BV407_V2_streaming'},
            {'text': '超自然音色-燃燃', 'value': 'BV407_streaming'},
            {'text': '通用女声', 'value': 'BV001_streaming'},
            {'text': '通用男声', 'value': 'BV002_streaming'},
        ])
    speed_ratio = forms.SliderField(
        TooltipLabel('语速', '[0.2,3]，默认为1，通常保留一位小数即可'),
        required=True, default_value=1,
        _min=0.2,
        _max=3,
        _step=0.1,
        precision=1)


class VolcanicEngineTTSModelCredential(BaseForm, BaseModelCredential):
    volcanic_api_url = forms.TextInputField('API 域名', required=True, default_value='wss://openspeech.bytedance.com/api/v1/tts/ws_binary')
    volcanic_app_id = forms.TextInputField('App ID', required=True)
    volcanic_token = forms.PasswordInputField('Access Token', required=True)
    volcanic_cluster = forms.TextInputField('Cluster ID', required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')

        for key in ['volcanic_api_url', 'volcanic_app_id', 'volcanic_token', 'volcanic_cluster']:
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
        return {**model, 'volcanic_token': super().encryption(model.get('volcanic_token', ''))}

    def get_model_params_setting_form(self, model_name):
        return VolcanicEngineTTSModelGeneralParams()
