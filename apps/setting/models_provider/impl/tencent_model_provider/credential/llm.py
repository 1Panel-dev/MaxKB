# coding=utf-8
from langchain_core.messages import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode
from django.utils.translation import gettext_lazy as _

class TencentLLMModelParams(BaseForm):
    temperature = forms.SliderField(TooltipLabel(_('Temperature'), _('Higher values make the output more random, while lower values make it more focused and deterministic')),
                                    required=True, default_value=0.5,
                                    _min=0.1,
                                    _max=2.0,
                                    _step=0.01,
                                    precision=2)


class TencentLLMModelCredential(BaseForm, BaseModelCredential):
    REQUIRED_FIELDS = ['hunyuan_app_id', 'hunyuan_secret_id', 'hunyuan_secret_key']

    @classmethod
    def _validate_model_type(cls, model_type, provider, raise_exception=False):
        if not any(mt['value'] == model_type for mt in provider.get_model_type_list()):
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, _('{model_type} Model type is not supported').format(model_type=model_type))
            return False
        return True

    @classmethod
    def _validate_credential_fields(cls, model_credential, raise_exception=False):
        missing_keys = [key for key in cls.REQUIRED_FIELDS if key not in model_credential]
        if missing_keys:
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, _('{keys} is required').format(keys=", ".join(missing_keys)))
            return False
        return True

    def is_valid(self, model_type, model_name, model_credential, model_params, provider,  raise_exception=False):
        if not (self._validate_model_type(model_type, provider, raise_exception) and
                self._validate_credential_fields(model_credential, raise_exception)):
            return False
        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            model.invoke([HumanMessage(content=_('Hello'))])
        except Exception as e:
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, _('Verification failed, please check whether the parameters are correct: {error}').format(error=str(e)))
            return False
        return True

    def encryption_dict(self, model):
        return {**model, 'hunyuan_secret_key': super().encryption(model.get('hunyuan_secret_key', ''))}

    hunyuan_app_id = forms.TextInputField('APP ID', required=True)
    hunyuan_secret_id = forms.PasswordInputField('SecretId', required=True)
    hunyuan_secret_key = forms.PasswordInputField('SecretKey', required=True)

    def get_model_params_setting_form(self, model_name):
        return TencentLLMModelParams()
