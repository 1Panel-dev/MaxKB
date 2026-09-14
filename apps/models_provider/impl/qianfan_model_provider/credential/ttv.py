# coding=utf-8
"""
@project: MaxKB
@file： ttv.py
@desc: 千帆视频生成模型凭据
"""

from typing import Dict, Any

from django.utils.translation import gettext, gettext_lazy as _

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, SliderField, TooltipLabel
from common.forms.switch_field import SwitchField
from models_provider.base_model_provider import BaseModelCredential, ValidCode


class QianfanVideoModelParams(BaseForm):
    duration = SliderField(
        TooltipLabel(
            _("Video duration"),
            _("The duration of the generated video in seconds. Only supported values are accepted."),
        ),
        required=False,
        default_value=None,
        _min=1,
        _max=30,
        _step=1,
        precision=0,
    )

    watermark = SwitchField(
        TooltipLabel(_("Watermark"), _("Whether the generated video contains a watermark")),
        attrs={"active-value": True, "inactive-value": False},
        default_value=False,
    )

    prompt_extend = SwitchField(
        TooltipLabel(_("Prompt extend"), _("Whether to use a large model to rewrite the prompt")),
        attrs={"active-value": True, "inactive-value": False},
        default_value=True,
    )


class QianfanVideoModelCredential(BaseForm, BaseModelCredential):
    api_base = forms.TextInputField("API URL", required=True, default_value="https://qianfan.baidubce.com/v2")
    api_key = forms.PasswordInputField("API Key", required=True)

    def is_valid(
        self,
        model_type: str,
        model_name,
        model_credential: Dict[str, Any],
        model_params,
        provider,
        raise_exception=False,
    ):
        for key in ["api_base", "api_key"]:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, gettext("{key}  is required").format(key=key))
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, "api_key": super().encryption(model.get("api_key", ""))}

    def get_model_params_setting_form(self, model_name):
        return QianfanVideoModelParams()
