# coding=utf-8

from typing import Dict, Any

from django.utils.translation import gettext_lazy as _, gettext

from common.exception.app_exception import AppApiException
from common.forms import BaseForm, PasswordInputField, SingleSelect, SliderField, TooltipLabel
from common.forms.switch_field import SwitchField
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from common.utils.logger import maxkb_logger

class QwenModelParams(BaseForm):
    """
    Parameters class for the Qwen Text-to-Video model.
    Defines fields such as Video size, number of Videos, and style.
    """

    size = SingleSelect(
        TooltipLabel(_('Video size'), _('Specify the size of the generated Video, such as: 1024x1024')),
        required=True,
        default_value='1280*720',
        option_list=[
            {'value': '832*480', 'label': '832*480'},
            {'value': '480*832', 'label': '480*832'},
            {'value': '1280*720', 'label': '1280*720'},
            {'value': '720*1280', 'label': '720*1280'},
        ],
        text_field='label',
        value_field='value'
    )

    watermark = SwitchField(
        TooltipLabel(_('Watermark'), _('Whether to add watermark')),
        attrs={"active-value": "true", "inactive-value": "false"},
        default_value=False,
    )


class TextToVideoModelCredential(BaseForm, BaseModelCredential):
    """
    Credential class for the Qwen Text-to-Video model.
    Provides validation and encryption for the model credentials.
    """

    api_key = PasswordInputField('API Key', required=True)

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

        :param model_type: Type of the model (e.g., 'TEXT_TO_Video').
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
                gettext('{model_type} Model type is not supported').format(model_type=model_type)
            )

        required_keys = ['api_key']
        for key in required_keys:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(
                        ValidCode.valid_error.value,
                        gettext('{key} is required').format(key=key)
                    )
                return False

        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            res = model.check_auth()
        except Exception as e:
            maxkb_logger.error(f'Exception: {e}', exc_info=True)
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(
                    ValidCode.valid_error.value,
                    gettext(
                        'Verification failed, please check whether the parameters are correct: {error}'
                    ).format(error=str(e))
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
        :return: Parameter setting form.
        """
        return QwenModelParams()
