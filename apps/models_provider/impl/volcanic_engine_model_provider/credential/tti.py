# coding=utf-8
from typing import Dict

from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from common.utils.logger import maxkb_logger

class VolcanicEngineTTIModelGeneralParams(BaseForm):
    size = forms.SingleSelect(
        TooltipLabel(_('Image size'),
                     _('If the gap between width, height and 512 is too large, the picture rendering effect will be poor and the probability of excessive delay will increase significantly. Recommended ratio and corresponding width and height before super score: width*height')),
        required=True,
        default_value='512x512',
        option_list=[
            {'label': '512x512', 'value': '512x512'},
            {'label': '1024x1024', 'value': '1024x1024'},
            {'label': '864x1152', 'value': '864x1152'},
            {'label': '1152x864', 'value': '1152x864'},
            {'label': '1280x720', 'value': '1280x720'},
            {'label': '720x1280', 'value': '720x1280'},
            {'label': '832x1248', 'value': '832x1248'},
            {'label': '1248x832', 'value': '1248x832'},
            {'label': '1512x648', 'value': '1512x648'},

        ],
        text_field='label',
        value_field='value')


class VolcanicEngineTTIModelCredential(BaseForm, BaseModelCredential):
    api_key = forms.PasswordInputField('Api key', required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  gettext('{model_type} Model type is not supported').format(model_type=model_type))

        for key in ['api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, gettext('{key}  is required').format(key=key))
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            model.check_auth()
        except Exception as e:
            maxkb_logger.error(f'Exception: {e}', exc_info=True)
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
        return {**model, 'api_key': super().encryption(model.get('api_key', ''))}

    def get_model_params_setting_form(self, model_name):
        return VolcanicEngineTTIModelGeneralParams()
