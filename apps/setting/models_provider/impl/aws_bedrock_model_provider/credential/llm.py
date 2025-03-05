import traceback
from typing import Dict

from django.utils.translation import gettext_lazy as _, gettext
from langchain_core.messages import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import ValidCode, BaseModelCredential


class BedrockLLMModelParams(BaseForm):
    temperature = forms.SliderField(TooltipLabel(_('Temperature'),
                                                 _('Higher values make the output more random, while lower values make it more focused and deterministic')),
                                    required=True, default_value=0.7,
                                    _min=0.1,
                                    _max=1.0,
                                    _step=0.01,
                                    precision=2)

    max_tokens = forms.SliderField(
        TooltipLabel(_('Output the maximum Tokens'),
                     _('Specify the maximum number of tokens that the model can generate')),
        required=True, default_value=1024,
        _min=1,
        _max=100000,
        _step=1,
        precision=0)


class BedrockLLMModelCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(mt.get('value') == model_type for mt in model_type_list):
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value,
                                      gettext('{model_type} Model type is not supported').format(model_type=model_type))
            return False

        required_keys = ['region_name', 'access_key_id', 'secret_access_key']
        if not all(key in model_credential for key in required_keys):
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value,
                                      gettext('The following fields are required: {keys}').format(
                                          keys=", ".join(required_keys)))
            return False

        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            model.invoke([HumanMessage(content=gettext('Hello'))])
        except AppApiException:
            raise
        except Exception as e:
            traceback.print_exc()
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value,
                                      gettext(
                                          'Verification failed, please check whether the parameters are correct: {error}').format(
                                          error=str(e)))
            return False

        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'secret_access_key': super().encryption(model.get('secret_access_key', ''))}

    region_name = forms.TextInputField('Region Name', required=True)
    access_key_id = forms.TextInputField('Access Key ID', required=True)
    secret_access_key = forms.PasswordInputField('Secret Access Key', required=True)
    base_url = forms.TextInputField('Proxy URL', required=False)

    def get_model_params_setting_form(self, model_name):
        return BedrockLLMModelParams()
