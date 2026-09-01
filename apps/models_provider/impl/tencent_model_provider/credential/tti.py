# coding=utf-8

from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from common.forms.switch_field import SwitchField
from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import BaseModelCredential, ValidCode

# 37 preset sizes from the TokenHub Hy-Image docs (width x height, area <= 1024x1024).
_HY_IMAGE_SIZES = [
    "2048x512",
    "1984x512",
    "1920x512",
    "1856x512",
    "1792x512",
    "1728x512",
    "1664x512",
    "1600x512",
    "1536x512",
    "1472x576",
    "1408x640",
    "1344x704",
    "1280x768",
    "1216x832",
    "1152x896",
    "1088x960",
    "1024x1024",
    "960x1088",
    "896x1152",
    "832x1216",
    "768x1280",
    "704x1344",
    "640x1408",
    "576x1472",
    "512x1536",
    "512x1600",
    "512x1664",
    "512x1728",
    "512x1792",
    "512x1856",
    "512x1920",
    "512x1984",
    "512x2048",
    "768x1024",
    "720x1280",
    "1024x768",
    "1280x720",
]


class TencentTTIModelParams(BaseForm):
    size = forms.SingleSelect(
        TooltipLabel(
            _("Image size"),
            _(
                "Width and height must be in [512, 2048] and the area must not exceed 1024x1024. If not passed, the "
                "model auto-selects the closest preset size."
            ),
        ),
        required=False,
        default_value="1024x1024",
        option_list=[{"value": value, "label": value} for value in _HY_IMAGE_SIZES],
        value_field="value",
        text_field="label",
    )

    revise = SwitchField(
        TooltipLabel(
            _("Prompt rewrite"), _("Whether the model should rewrite and optimize the prompt before generation.")
        ),
        attrs={"active-value": True, "inactive-value": False},
        default_value=True,
    )

    footnote = forms.TextInputField(
        TooltipLabel(
            _("Watermark footnote"), _("Custom watermark content, at most 16 characters, drawn in the bottom-right.")
        ),
        required=False,
        default_value="",
    )


class TencentTTIModelCredential(BaseForm, BaseModelCredential):
    REQUIRED_FIELDS = ["api_key"]

    @classmethod
    def _validate_model_type(cls, model_type, provider, raise_exception=False):
        if not any(mt["value"] == model_type for mt in provider.get_model_type_list()):
            if raise_exception:
                raise AppApiException(
                    ValidCode.valid_error.value,
                    gettext("{model_type} Model type is not supported").format(model_type=model_type),
                )
            return False
        return True

    @classmethod
    def _validate_credential_fields(cls, model_credential, raise_exception=False):
        missing_keys = [key for key in cls.REQUIRED_FIELDS if key not in model_credential]
        if missing_keys:
            if raise_exception:
                raise AppApiException(
                    ValidCode.valid_error.value, gettext("{keys} is required").format(keys=", ".join(missing_keys))
                )
            return False
        return True

    def is_valid(self, model_type, model_name, model_credential, model_params, provider, raise_exception=False):
        if not (
            self._validate_model_type(model_type, provider, raise_exception)
            and self._validate_credential_fields(model_credential, raise_exception)
        ):
            return False
        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            model.check_auth()
        except Exception as e:
            maxkb_logger.error(f"Exception: {e}", exc_info=True)
            if raise_exception:
                raise AppApiException(
                    ValidCode.valid_error.value,
                    gettext("Verification failed, please check whether the parameters are correct: {error}").format(
                        error=str(e)
                    ),
                )
            return False
        return True

    def encryption_dict(self, model):
        return {**model, "api_key": super().encryption(model.get("api_key", ""))}

    base_url = forms.TextInputField(
        label=TooltipLabel(_("API URL"), _("TokenHub Hy-Image v3-generation endpoint")),
        required=False,
        default_value="https://tokenhub.tencentmaas.com/v1/wand/hunyuan-image/v3-generation",
    )
    api_key = forms.PasswordInputField(_("API Key"), required=True)

    def get_model_params_setting_form(self, model_name):
        return TencentTTIModelParams()
