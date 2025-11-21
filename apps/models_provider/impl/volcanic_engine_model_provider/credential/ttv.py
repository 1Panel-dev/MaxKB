# coding=utf-8
from typing import Dict

from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel, SingleSelect, TextInputField
from common.forms.switch_field import SwitchField
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from common.utils.logger import maxkb_logger

class VolcanicEngineTTVModelGeneralParams(BaseForm):
    resolution = SingleSelect(
        TooltipLabel(_('Resolution'), _('Resolution')),
        required=True,
        default_value='480P',
        option_list=[
            {'value': '480P', 'label': '480P'},
            {'value': '720P', 'label': '720P'},
            {'value': '1080P', 'label': '1080P'},
        ],
        text_field='label',
        value_field='value'
    )
    ratio = SingleSelect(
        TooltipLabel(_('Ratio'), _('Ratio')),
        required=True,
        default_value='16:9',
        option_list=[
            {'value': '16:9', 'label': '16:9'},
            {'value': '9:16', 'label': '9:16'},
            {'value': '1:1', 'label': '1:1'},
            {'value': '4:3', 'label': '4:3'},
            {'value': '3:4', 'label': '3:4'},
            {'value': '21:9', 'label': '21:9'},
        ],
        text_field='label',
        value_field='value'
    )
    duration = TextInputField(
        TooltipLabel(_('Duration'), _('Duration')),
        required=True,
        default_value=5,
    )

    watermark = SwitchField(
        TooltipLabel(_('Watermark'), _('Whether to add watermark')),
        attrs={"active-value": "true", "inactive-value": "false"},
        default_value=False,
    )


class VolcanicEngineTTVModelCredential(BaseForm, BaseModelCredential):
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
        return VolcanicEngineTTVModelGeneralParams()
