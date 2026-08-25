# coding=utf-8
"""
@project: MaxKB
@desc: Tencent Tokenhub ASR sync_transcribe credential (model: wand-asr-v1 / hy-asr-3.0-preview)
"""

from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import BaseModelCredential, ValidCode


class TencentTokenhubSTTModelParams(BaseForm):
    source = forms.SingleSelect(
        label=TooltipLabel(_("Recognition language"), _("Recognition language: zh / en, auto detected when omitted")),
        text_field="value",
        value_field="value",
        option_list=[
            {"value": "", "label": _("Auto detect")},
            {"value": "zh", "label": _("Chinese")},
            {"value": "en", "label": _("English")},
        ],
        required=False,
        default_value="",
    )
    voice_encode_format = forms.SingleSelect(
        label=TooltipLabel(_("Audio encoding"), _("pcm / wav / ogg / mp3, auto detected when omitted")),
        text_field="value",
        value_field="value",
        option_list=[
            {"value": "", "label": _("Auto")},
            {"value": "pcm", "label": "pcm"},
            {"value": "wav", "label": "wav"},
            {"value": "ogg", "label": "ogg"},
            {"value": "mp3", "label": "mp3"},
        ],
        required=False,
        default_value="",
    )


class TencentTokenhubSTTModelCredential(BaseForm, BaseModelCredential):
    def is_valid(self, model_type, model_name, model_credential, model_params, provider, raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get("value") == model_type, model_type_list))):
            raise AppApiException(
                ValidCode.valid_error.value,
                gettext("{model_type} Model type is not supported").format(model_type=model_type),
            )
        if "api_key" not in model_credential:
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, gettext("{key} is required").format(key="api_key"))
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
        label=TooltipLabel(_("API URL"), _("Tokenhub sync_transcribe endpoint")),
        required=False,
        default_value="https://tokenhub.tencentmaas.com/v1/wand/asrproxy/sync_transcribe",
    )
    api_key = forms.PasswordInputField(_("API Key"), required=True)

    def get_model_params_setting_form(self, model_name):
        return TencentTokenhubSTTModelParams()
