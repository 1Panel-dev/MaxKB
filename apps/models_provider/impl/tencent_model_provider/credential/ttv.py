# coding=utf-8

from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from common.forms.switch_field import SwitchField
from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import BaseModelCredential, ValidCode


class TencentVideoModelParams(BaseForm):
    resolution = forms.SingleSelect(
        TooltipLabel(_("Resolution"), _("Output video resolution: 480p, 720p, 1080p.")),
        required=False,
        default_value="720p",
        option_list=[{"value": value, "label": value} for value in ["480p", "720p", "1080p"]],
        value_field="value",
        text_field="label",
    )

    fps = forms.SingleSelect(
        TooltipLabel(_("Frame rate"), _("Output video frame rate: 16, 24, 30.")),
        required=False,
        default_value="30",
        option_list=[{"value": value, "label": value} for value in ["16", "24", "30"]],
        value_field="value",
        text_field="label",
    )

    logo_add = SwitchField(
        TooltipLabel(
            _("Add logo"),
            _(
                "Whether to add the AI-generated logo to the video. 1: add logo; 0: no logo "
                "(requires console approval for independent control)."
            ),
        ),
        attrs={"active-value": 1, "inactive-value": 0},
        default_value=1,
    )


class TencentTTVModelCredential(BaseForm, BaseModelCredential):
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
        label=TooltipLabel(
            _("API URL"),
            _(
                "TokenHub video endpoint. Use the base (e.g. https://tokenhub.tencentmaas.com/v1) or a full submit/query URL."
            ),
        ),
        required=False,
        default_value="https://tokenhub.tencentmaas.com/v1",
    )
    api_key = forms.PasswordInputField(_("API Key"), required=True)

    def get_model_params_setting_form(self, model_name):
        return TencentVideoModelParams()
