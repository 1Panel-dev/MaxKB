# coding=utf-8

from typing import Dict, Any

from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, PasswordInputField, TooltipLabel
from common.forms.switch_field import SwitchField
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from common.utils.logger import maxkb_logger


class MiniMaxModelParams(BaseForm):
    """
    Parameters class for the MiniMax V1 (legacy) Video model.
    """

    aigc_watermark = SwitchField(
        TooltipLabel(_("Watermark"), _("Whether to add watermark")),
        attrs={"active-value": True, "inactive-value": False},
        default_value=False,
    )


class MiniMaxH3ModelParams(BaseForm):
    """
    Parameters class for the MiniMax V2 (MiniMax-H3) Video model.
    """

    resolution = forms.SingleSelect(
        TooltipLabel(_("Resolution"), _("Output video resolution.")),
        required=True,
        default_value="480P",
        option_list=[{"value": value, "label": value} for value in ["480P", "768P", "2K"]],
        text_field="label",
        value_field="value",
    )

    duration = forms.SliderField(
        TooltipLabel(_("Duration"), _("Video duration in seconds (4-15).")),
        4,
        15,
        1,
        0,
        required=True,
        default_value=10,
    )

    ratio = forms.SingleSelect(
        TooltipLabel(_("Aspect ratio"), _("Output video aspect ratio.")),
        required=False,
        default_value="16:9",
        option_list=[{"value": value, "label": value} for value in ["16:9", "9:16", "1:1", "4:3", "3:4"]],
        text_field="label",
        value_field="value",
    )


class TextToVideoModelCredential(BaseForm, BaseModelCredential):
    """
    Credential class for the Qwen Text-to-Video model.
    Provides validation and encryption for the model credentials.
    """

    api_base = forms.TextInputField("API URL", required=True, default_value="https://api.minimaxi.com/v1")
    api_key = PasswordInputField("API Key", required=True)

    def is_valid(
        self,
        model_type: str,
        model_name: str,
        model_credential: Dict[str, Any],
        model_params: Dict[str, Any],
        provider,
        raise_exception: bool = False,
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
        if not any(mt.get("value") == model_type for mt in model_type_list):
            raise AppApiException(
                ValidCode.valid_error.value,
                gettext("{model_type} Model type is not supported").format(model_type=model_type),
            )

        required_keys = ["api_key", "api_base"]
        for key in required_keys:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, gettext("{key} is required").format(key=key))
                return False

        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            res = model.check_auth()
        except Exception as e:
            maxkb_logger.error(f"Exception: {e}", exc_info=True)
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(
                    ValidCode.valid_error.value,
                    gettext("Verification failed, please check whether the parameters are correct: {error}").format(
                        error=str(e)
                    ),
                )
            return False

        return True

    def encryption_dict(self, model: Dict[str, object]) -> Dict[str, object]:
        """
        Encrypt sensitive fields in the model dictionary.

        :param model: Dictionary containing model details.
        :return: Dictionary with encrypted sensitive fields.
        """
        return {**model, "api_key": super().encryption(model.get("api_key", ""))}

    def get_model_params_setting_form(self, model_name: str):
        """
        Get the parameter setting form for the specified model.

        :param model_name: Name of the model.
        :return: Parameter setting form.
        """
        return MiniMaxModelParams()


class MiniMaxH3TextToVideoModelCredential(TextToVideoModelCredential):
    """
    Credential for the MiniMax H3 / H3-Max (V2) text-to-video model.
    Uses the V2 endpoint and requires resolution / duration / ratio.
    """

    # BaseForm 只收集本类的字段（vars(self.__class__) 不走 MRO），继承字段需重新声明
    api_base = forms.TextInputField("API URL", required=True, default_value="https://api.minimaxi.com/v2")
    api_key = PasswordInputField("API Key", required=True)

    def get_model_params_setting_form(self, model_name: str):
        return MiniMaxH3ModelParams()
