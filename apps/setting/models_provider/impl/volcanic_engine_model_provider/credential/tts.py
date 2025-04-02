# coding=utf-8
import traceback
from typing import Dict

from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class VolcanicEngineTTSModelGeneralParams(BaseForm):
    voice_type = forms.SingleSelect(
        TooltipLabel(_('timbre'), _('Chinese sounds can support mixed scenes of Chinese and English')),
        required=True, default_value='zh_female_cancan_mars_bigtts',
        text_field='value',
        value_field='value',
        option_list=[
            {'text': '灿灿/Shiny', 'value': 'zh_female_cancan_mars_bigtts'},
            {'text': '清新女声', 'value': 'zh_female_qingxinnvsheng_mars_bigtts'},
            {'text': '爽快思思/Skye', 'value': 'zh_female_shuangkuaisisi_moon_bigtts'},
            {'text': '湾区大叔', 'value': 'zh_female_wanqudashu_moon_bigtts' },
            {'text': '呆萌川妹', 'value': 'zh_female_daimengchuanmei_moon_bigtts'},
            {'text': '广州德哥', 'value': 'zh_male_guozhoudege_moon_bigtts'},
            {'text': '北京小爷', 'value': 'zh_male_beijingxiaoye_moon_bigtts'},
            {'text': '少年梓辛/Brayan', 'value': 'zh_male_shaonianzixin_moon_bigtts'},
            {'text': '魅力女友', 'value': 'zh_female_meilinvyou_moon_bigtts'},
        ])
    speed_ratio = forms.SliderField(
        TooltipLabel(_('speaking speed'), _('[0.2,3], the default is 1, usually one decimal place is enough')),
        required=True, default_value=1,
        _min=0.2,
        _max=3,
        _step=0.1,
        precision=1)


class VolcanicEngineTTSModelCredential(BaseForm, BaseModelCredential):
    volcanic_api_url = forms.TextInputField('API URL', required=True,
                                            default_value='wss://openspeech.bytedance.com/api/v1/tts/ws_binary')
    volcanic_app_id = forms.TextInputField('App ID', required=True)
    volcanic_token = forms.PasswordInputField('Access Token', required=True)
    volcanic_cluster = forms.TextInputField('Cluster ID', required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  gettext('{model_type} Model type is not supported').format(model_type=model_type))

        for key in ['volcanic_api_url', 'volcanic_app_id', 'volcanic_token', 'volcanic_cluster']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, gettext('{key}  is required').format(key=key))
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            model.check_auth()
        except Exception as e:
            traceback.print_exc()
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, gettext(
                    'Verification failed, please check whether the parameters are correct: {error}').format(
                    error=str(e)))
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'volcanic_token': super().encryption(model.get('volcanic_token', ''))}

    def get_model_params_setting_form(self, model_name):
        return VolcanicEngineTTSModelGeneralParams()
