# coding=utf-8
import traceback
from typing import Dict

from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class VolcanicEngineTTIModelGeneralParams(BaseForm):
    size = forms.SingleSelect(
        TooltipLabel(_('Image size'),
                     _('If the gap between width, height and 512 is too large, the picture rendering effect will be poor and the probability of excessive delay will increase significantly. Recommended ratio and corresponding width and height before super score: width*height')),
        required=True,
        default_value='512*512',
        option_list=[
            {'value': '512*512', 'label': '512*512'},
            {'value': '512*384', 'label': '512*384'},
            {'value': '384*512', 'label': '384*512'},
            {'value': '512*341', 'label': '512*341'},
            {'value': '341*512', 'label': '341*512'},
            {'value': '512*288', 'label': '512*288'},
            {'value': '288*512', 'label': '288*512'},
        ],
        text_field='label',
        value_field='value')


class VolcanicEngineTTIModelCredential(BaseForm, BaseModelCredential):
    access_key = forms.PasswordInputField('Access Key ID', required=True)
    secret_key = forms.PasswordInputField('Secret Access Key', required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  gettext('{model_type} Model type is not supported').format(model_type=model_type))

        for key in ['access_key', 'secret_key']:
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
        return {**model, 'secret_key': super().encryption(model.get('secret_key', ''))}

    def get_model_params_setting_form(self, model_name):
        return VolcanicEngineTTIModelGeneralParams()
