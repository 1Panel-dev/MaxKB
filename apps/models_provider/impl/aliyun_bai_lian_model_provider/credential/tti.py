# coding=utf-8

from typing import Dict, Any

from django.utils.translation import gettext_lazy as _, gettext

from common.exception.app_exception import AppApiException
from common.forms import BaseForm, PasswordInputField, SingleSelect, SliderField, TooltipLabel
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from common.utils.logger import maxkb_logger


class QwenModelParams(BaseForm):
    """
    Parameters class for the Qwen Text-to-Image model.
    Defines fields such as image size, number of images, and style.
    """

    size = SingleSelect(
        TooltipLabel(_('Image size'), _('Specify the size of the generated image, such as: 1024x1024')),
        required=True,
        default_value='1024*1024',
        option_list=[
            {'value': '1024*1024', 'label': '1024*1024'},
            {'value': '720*1280', 'label': '720*1280'},
            {'value': '768*1152', 'label': '768*1152'},
            {'value': '1280*720', 'label': '1280*720'},
        ],
        text_field='label',
        value_field='value',
        attrs={'allow-create': True, 'filterable': True}
    )

    n = SliderField(
        TooltipLabel(_('Number of pictures'), _('Specify the number of generated images')),
        required=True,
        default_value=1,
        _min=1,
        _max=4,
        _step=1,
        precision=0
    )

    style = SingleSelect(
        TooltipLabel(_('Style'), _('Specify the style of generated images')),
        required=True,
        default_value='<auto>',
        option_list=[
            {'value': '<auto>', 'label': _('Default value, the image style is randomly output by the model')},
            {'value': '<photography>', 'label': _('photography')},
            {'value': '<portrait>', 'label': _('Portraits')},
            {'value': '<3d cartoon>', 'label': _('3D cartoon')},
            {'value': '<anime>', 'label': _('animation')},
            {'value': '<oil painting>', 'label': _('painting')},
            {'value': '<watercolor>', 'label': _('watercolor')},
            {'value': '<sketch>', 'label': _('sketch')},
            {'value': '<chinese painting>', 'label': _('Chinese painting')},
            {'value': '<flat illustration>', 'label': _('flat illustration')},
        ],
        text_field='label',
        value_field='value'
    )


class QwenTextToImageModelCredential(BaseForm, BaseModelCredential):
    """
    Credential class for the Qwen Text-to-Image model.
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

        :param model_type: Type of the model (e.g., 'TEXT_TO_IMAGE').
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
