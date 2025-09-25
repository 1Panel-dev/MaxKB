import traceback

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from django.utils.translation import gettext_lazy as _, gettext

from models_provider.base_model_provider import BaseModelCredential, ValidCode


class TencentSSTModelParams(BaseForm):
    EngSerViceType = forms.SingleSelect(
        TooltipLabel(_('Engine model type'), _('If not passed, the default value is 16k_zh (Chinese universal)')),
        required=True,
        default_value='16k_zh',
        option_list=[
            {"value": "8k_zh", "label": _("Chinese telephone universal")},
            {"value": "8k_en", "label": _("English telephone universal")},
            {"value": "16k_zh", "label": _("Commonly used in Chinese")},
            {"value": "16k_zh-PY", "label": _("Chinese, English, and Guangdong")},
            {"value": "16k_zh_medical", "label": _("Chinese medical")},
            {"value": "16k_en", "label": _("English")},
            {"value": "16k_yue", "label": _("Cantonese")},
            {"value": "16k_ja", "label": _("Japanese")},
            {"value": "16k_ko", "label": _("Korean")},
            {"value": "16k_vi", "label": _("Vietnamese")},
            {"value": "16k_ms", "label": _("Malay language")},
            {"value": "16k_id", "label": _("Indonesian language")},
            {"value": "16k_fil", "label": _("Filipino language")},
            {"value": "16k_th", "label": _("Thai")},
            {"value": "16k_pt", "label": _("Portuguese")},
            {"value": "16k_tr", "label": _("Turkish")},
            {"value": "16k_ar", "label": _("Arabic")},
            {"value": "16k_es", "label": _("Spanish")},
            {"value": "16k_hi", "label": _("Hindi")},
            {"value": "16k_fr", "label": _("French")},
            {"value": "16k_de", "label": _("German")},
            {"value": "16k_zh_dialect", "label": _("Multiple dialects, supporting 23 dialects")}
        ],
        value_field='value',
        text_field='label'
    )

class TencentSTTModelCredential(BaseForm, BaseModelCredential):
    REQUIRED_FIELDS = ["SecretId", "SecretKey"]

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
        return {**model, 'SecretKey': super().encryption(model.get('SecretKey', ''))}

    SecretId = forms.PasswordInputField('SecretId', required=True)
    SecretKey = forms.PasswordInputField('SecretKey', required=True)

    def get_model_params_setting_form(self, model_name):
        return TencentSSTModelParams()
