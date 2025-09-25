# coding=utf-8
import traceback
from typing import Dict, Any

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, PasswordInputField, TooltipLabel
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from django.utils.translation import gettext as _

class AliyunBaiLianOmiSTTModelParams(BaseForm):
    CueWord = forms.TextInputField(
        TooltipLabel(_('CueWord'), _('If not passed, the default value is What is this audio saying? Only answer the audio content')),
        required=True,
        default_value='这段音频在说什么，只回答音频的内容',
    )


class AliyunBaiLianOmiSTTModelCredential(BaseForm, BaseModelCredential):
    api_url = forms.TextInputField(_('API URL'), required=True)
    api_key = forms.PasswordInputField(_('API Key'), required=True)

    def is_valid(self,
                 model_type: str,
                 model_name: str,
                 model_credential: Dict[str, Any],
                 model_params: Dict[str, Any],
                 provider,
                 raise_exception: bool = False
                 ) -> bool:

        model_type_list = provider.get_model_type_list()
        if not any(mt.get('value') == model_type for mt in model_type_list):
            raise AppApiException(
                ValidCode.valid_error.value,
                _('{model_type} Model type is not supported').format(model_type=model_type)
            )

        required_keys = ['api_key']
        for key in required_keys:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(
                        ValidCode.valid_error.value,
                        _('{key} is required').format(key=key)
                    )
                return False

        try:
            model = provider.get_model(model_type, model_name, model_credential)
        except Exception as e:
            traceback.print_exc()
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(
                ValidCode.valid_error.value,
                _('Verification failed, please check whether the parameters are correct: {error}').format(error=str(e))
                )
            return False
        return True

    def encryption_dict(self, model: Dict[str, object]) -> Dict[str, object]:

        return {
            **model,
            'api_key': super().encryption(model.get('api_key', ''))
        }


    def get_model_params_setting_form(self, model_name):

        return AliyunBaiLianOmiSTTModelParams()