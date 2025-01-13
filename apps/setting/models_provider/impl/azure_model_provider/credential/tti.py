# coding=utf-8
from typing import Dict

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode
from django.utils.translation import gettext_lazy as _


class AzureOpenAITTIModelParams(BaseForm):
    size = forms.SingleSelect(
        TooltipLabel(_('Image size'), _('Specify the size of the generated image, such as: 1024x1024')),
        required=True,
        default_value='1024x1024',
        option_list=[
            {'value': '1024x1024', 'label': '1024x1024'},
            {'value': '1024x1792', 'label': '1024x1792'},
            {'value': '1792x1024', 'label': '1792x1024'},
        ],
        text_field='label',
        value_field='value'
    )

    quality = forms.SingleSelect(
        TooltipLabel(_('Picture quality'), ''),
        required=True,
        default_value='standard',
        option_list=[
            {'value': 'standard', 'label': 'standard'},
            {'value': 'hd', 'label': 'hd'},
        ],
        text_field='label',
        value_field='value'
    )

    n = forms.SliderField(
        TooltipLabel(_('Number of pictures'), _('Specify the number of generated images')),
        required=True, default_value=1,
        _min=1,
        _max=10,
        _step=1,
        precision=0)


class AzureOpenAITextToImageModelCredential(BaseForm, BaseModelCredential):
    api_version = forms.TextInputField("API Version", required=True)
    api_base = forms.TextInputField('Azure Endpoint', required=True)
    api_key = forms.PasswordInputField("API Key", required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, _('{model_type} Model type is not supported').format(model_type=model_type))

        for key in ['api_base', 'api_key', 'api_version']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, _('{key}  is required').format(key=key))
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            res = model.check_auth()
            print(res)
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, _('Verification failed, please check whether the parameters are correct: {error}').format(error=str(e)))
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'api_key': super().encryption(model.get('api_key', ''))}

    def get_model_params_setting_form(self, model_name):
        return AzureOpenAITTIModelParams()
