# coding=utf-8
import traceback

from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class TencentTTIModelParams(BaseForm):
    Style = forms.SingleSelect(
        TooltipLabel(_('painting style'), _('If not passed, the default value is 201 (Japanese anime style)')),
        required=True,
        default_value='201',
        option_list=[
            {'value': '000', 'label': _('Not limited to style')},
            {'value': '101', 'label': _('ink painting')},
            {'value': '102', 'label': _('concept art')},
            {'value': '103', 'label': _('Oil painting 1')},
            {'value': '118', 'label': _('Oil Painting 2 (Van Gogh)')},
            {'value': '104', 'label': _('watercolor painting')},
            {'value': '105', 'label': _('pixel art')},
            {'value': '106', 'label': _('impasto style')},
            {'value': '107', 'label': _('illustration')},
            {'value': '108', 'label': _('paper cut style')},
            {'value': '109', 'label': _('Impressionism 1 (Monet)')},
            {'value': '119', 'label': _('Impressionism 2')},
            {'value': '110', 'label': '2.5D'},
            {'value': '111', 'label': _('classical portraiture')},
            {'value': '112', 'label': _('black and white sketch')},
            {'value': '113', 'label': _('cyberpunk')},
            {'value': '114', 'label': _('science fiction style')},
            {'value': '115', 'label': _('dark style')},
            {'value': '116', 'label': '3D'},
            {'value': '117', 'label': _('vaporwave')},
            {'value': '201', 'label': _('Japanese animation')},
            {'value': '202', 'label': _('monster style')},
            {'value': '203', 'label': _('Beautiful ancient style')},
            {'value': '204', 'label': _('retro anime')},
            {'value': '301', 'label': _('Game cartoon hand drawing')},
            {'value': '401', 'label': _('Universal realistic style')},
        ],
        value_field='value',
        text_field='label'
    )

    Resolution = forms.SingleSelect(
        TooltipLabel(_('Generate image resolution'), _('If not transmitted, the default value is 768:768.')),
        required=True,
        default_value='768:768',
        option_list=[
            {'value': '768:768', 'label': '768:768（1:1）'},
            {'value': '768:1024', 'label': '768:1024（3:4）'},
            {'value': '1024:768', 'label': '1024:768（4:3）'},
            {'value': '1024:1024', 'label': '1024:1024（1:1）'},
            {'value': '720:1280', 'label': '720:1280（9:16）'},
            {'value': '1280:720', 'label': '1280:720（16:9）'},
            {'value': '768:1280', 'label': '768:1280（3:5）'},
            {'value': '1280:768', 'label': '1280:768（5:3）'},
            {'value': '1080:1920', 'label': '1080:1920（9:16）'},
            {'value': '1920:1080', 'label': '1920:1080（16:9）'},
        ],
        value_field='value',
        text_field='label'
    )


class TencentTTIModelCredential(BaseForm, BaseModelCredential):
    REQUIRED_FIELDS = ['hunyuan_secret_id', 'hunyuan_secret_key']

    @classmethod
    def _validate_model_type(cls, model_type, provider, raise_exception=False):
        if not any(mt['value'] == model_type for mt in provider.get_model_type_list()):
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value,
                                      gettext('{model_type} Model type is not supported').format(model_type=model_type))
            return False
        return True

    @classmethod
    def _validate_credential_fields(cls, model_credential, raise_exception=False):
        missing_keys = [key for key in cls.REQUIRED_FIELDS if key not in model_credential]
        if missing_keys:
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value,
                                      gettext('{keys} is required').format(keys=", ".join(missing_keys)))
            return False
        return True

    def is_valid(self, model_type, model_name, model_credential, model_params, provider, raise_exception=False):
        if not (self._validate_model_type(model_type, provider, raise_exception) and
                self._validate_credential_fields(model_credential, raise_exception)):
            return False
        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            model.check_auth()
        except Exception as e:
            traceback.print_exc()
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value,
                                      gettext(
                                          'Verification failed, please check whether the parameters are correct: {error}').format(
                                          error=str(e)))
            return False
        return True

    def encryption_dict(self, model):
        return {**model, 'hunyuan_secret_key': super().encryption(model.get('hunyuan_secret_key', ''))}

    hunyuan_secret_id = forms.PasswordInputField('SecretId', required=True)
    hunyuan_secret_key = forms.PasswordInputField('SecretKey', required=True)

    def get_model_params_setting_form(self, model_name):
        return TencentTTIModelParams()
