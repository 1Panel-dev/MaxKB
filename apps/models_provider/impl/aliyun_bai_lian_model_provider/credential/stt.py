# coding=utf-8

import traceback
from typing import Dict, Any

from django.utils.translation import gettext as _

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, PasswordInputField, TooltipLabel
from models_provider.base_model_provider import BaseModelCredential, ValidCode


class AliyunBaiLianSTTModelParams(BaseForm):
    sample_rate = forms.SliderField(
        TooltipLabel(_('Sample Rate'), _('If not passed, the default value is 16000')),
        required=True,
        default_value=16000,
        _step=4000, _min=0, _max=20000,precision=0
    )

class AliyunBaiLianSTTModelCredential(BaseForm, BaseModelCredential):
    """
    Credential class for the Aliyun BaiLian STT (Speech-to-Text) model.
    Provides validation and encryption for the model credentials.
    """

    api_key = PasswordInputField("API Key", required=True)

    def is_valid(
        self,
        model_type: str,
        model_name: str,
        model_credential: Dict[str, Any],
        model_params: Dict[str, Any],
        provider,
        raise_exception: bool = False
    ) -> bool:
        """
        Validate the model credentials.

        :param model_type: Type of the model (e.g., 'STT').
        :param model_name: Name of the model.
        :param model_credential: Dictionary containing the model credentials.
        :param model_params: Parameters for the model.
        :param provider: Model provider instance.
        :param raise_exception: Whether to raise an exception on validation failure.
        :return: Boolean indicating whether the credentials are valid.
        """
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
            model = provider.get_model(model_type, model_name, model_credential,**model_params)
            model.check_auth()
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
        """
        Encrypt sensitive fields in the model dictionary.

        :param model: Dictionary containing model details.
        :return: Dictionary with encrypted sensitive fields.
        """
        return {
            **model,
            'api_key': super().encryption(model.get('api_key', ''))
        }

    def get_model_params_setting_form(self, model_name: str):
        """
        Get the parameter setting form for the specified model.

        :param model_name: Name of the model.
        :return: Parameter setting form (not implemented).
        """
        return AliyunBaiLianSTTModelParams()
