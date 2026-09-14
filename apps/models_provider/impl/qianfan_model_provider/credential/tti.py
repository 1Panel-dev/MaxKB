# coding=utf-8
"""
@project: MaxKB
@file： tti.py
@desc: 千帆文生图模型凭据
"""

from typing import Dict

from django.utils.translation import gettext, gettext_lazy as _

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import BaseModelCredential, ValidCode


class QianfanTTIModelParams(BaseForm):
    size = forms.SingleSelect(
        TooltipLabel(
            _("Image size"),
            _(
                "The size of the generated image. Optional values: [1024x1024, 1280x720, 720x1280, 1152x864, 864x1152, "
                "1328x1328, 1664x928, 928x1664, 1472x1104, 1104x1472], default is 1024x1024."
            ),
        ),
        required=True,
        default_value="1024x1024",
        option_list=[
            {"value": "1024x1024", "label": "1024x1024"},
            {"value": "1280x720", "label": "1280x720"},
            {"value": "720x1280", "label": "720x1280"},
            {"value": "1152x864", "label": "1152x864"},
            {"value": "864x1152", "label": "864x1152"},
            {"value": "1328x1328", "label": "1328x1328"},
            {"value": "1664x928", "label": "1664x928"},
            {"value": "928x1664", "label": "928x1664"},
            {"value": "1472x1104", "label": "1472x1104"},
            {"value": "1104x1472", "label": "1104x1472"},
        ],
        text_field="label",
        value_field="value",
    )

    response_format = forms.SingleSelect(
        TooltipLabel(
            _("Response format"),
            _("The format of the generated image. url returns a URL, b64_json returns base64-encoded data."),
        ),
        required=True,
        default_value="url",
        option_list=[
            {"value": "url", "label": "url"},
            {"value": "b64_json", "label": "b64_json"},
        ],
        text_field="label",
        value_field="value",
    )


class QianfanTextToImageModelCredential(BaseForm, BaseModelCredential):
    api_base = forms.TextInputField(
        "API URL",
        required=True,
        default_value="https://qianfan.baidubce.com/v2/musesteamer/images/generations",
    )
    api_key = forms.PasswordInputField("API Key", required=True)

    def is_valid(
        self,
        model_type: str,
        model_name,
        model_credential: Dict[str, object],
        model_params,
        provider,
        raise_exception=False,
    ):
        for key in ["api_base", "api_key"]:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, gettext("{key}  is required").format(key=key))
                return False

        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            model.check_auth()
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

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, "api_key": super().encryption(model.get("api_key", ""))}

    def get_model_params_setting_form(self, model_name):
        return QianfanTTIModelParams()
