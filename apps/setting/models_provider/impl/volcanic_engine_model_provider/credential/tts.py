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
        required=True, default_value='BV002_streaming',
        text_field='value',
        value_field='value',
        option_list=[
            {'text': 'CanCan 2.0', 'value': 'BV700_V2_streaming'},
            {'text': 'Yangyang', 'value': 'BV705_streaming'},
            {'text': 'Qingcang 2.0', 'value': 'BV701_V2_streaming'},
            {'text': _('Universal female voice'), 'value': 'BV001_V2_streaming'},
            {'text': 'CanCan', 'value': 'BV700_streaming'},
            {'text': _('Supernatural timbre-ZiZi 2.0'), 'value': 'BV406_V2_streaming'},
            {'text': _('Supernatural timbre-ZiZi'), 'value': 'BV406_streaming'},
            {'text': _('Supernatural sound-Ranran 2.0'), 'value': 'BV407_V2_streaming'},
            {'text': _('Supernatural sound-Ranran'), 'value': 'BV407_streaming'},
            {'text': _('Universal female voice'), 'value': 'BV001_streaming'},
            {'text': _('Universal male voice'), 'value': 'BV002_streaming'},
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
