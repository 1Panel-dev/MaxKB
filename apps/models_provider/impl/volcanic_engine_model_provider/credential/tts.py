# coding=utf-8
from typing import Dict

from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from common.utils.logger import maxkb_logger


class VolcanicEngineTTSModelGeneralParams(BaseForm):
    voice_type = forms.SingleSelect(
        TooltipLabel(_("timbre"), _("Chinese sounds can support mixed scenes of Chinese and English")),
        required=True,
        default_value="zh_female_cancan_mars_bigtts",
        text_field="label",
        value_field="value",
        option_list=[
            {"label": "灿灿/Shiny", "value": "zh_female_cancan_mars_bigtts"},
            {"label": "清新女声", "value": "zh_female_qingxinnvsheng_mars_bigtts"},
            {"label": "爽快思思/Skye", "value": "zh_female_shuangkuaisisi_moon_bigtts"},
            {"label": "湾区大叔", "value": "zh_female_wanqudashu_moon_bigtts"},
            {"label": "呆萌川妹", "value": "zh_female_daimengchuanmei_moon_bigtts"},
            {"label": "广州德哥", "value": "zh_male_guozhoudege_moon_bigtts"},
            {"label": "北京小爷", "value": "zh_male_beijingxiaoye_moon_bigtts"},
            {"label": "少年梓辛/Brayan", "value": "zh_male_shaonianzixin_moon_bigtts"},
            {"label": "魅力女友", "value": "zh_female_meilinvyou_moon_bigtts"},
        ],
    )
    format = forms.SingleSelect(
        TooltipLabel(_("audio format"), _("The streaming scenario recommends pcm")),
        required=True,
        default_value="mp3",
        text_field="label",
        value_field="value",
        option_list=[
            {"label": "mp3", "value": "mp3"},
            {"label": "pcm", "value": "pcm"},
            {"label": "ogg_opus", "value": "ogg_opus"},
            {"label": "wav", "value": "wav"},
        ],
    )
    sample_rate = forms.SingleSelect(
        TooltipLabel(_("sample rate"), _("ogg_opus only supports 48000")),
        required=True,
        default_value=24000,
        text_field="label",
        value_field="value",
        option_list=[
            {"label": "8000", "value": 8000},
            {"label": "16000", "value": 16000},
            {"label": "22050", "value": 22050},
            {"label": "24000", "value": 24000},
            {"label": "32000", "value": 32000},
            {"label": "44100", "value": 44100},
            {"label": "48000", "value": 48000},
        ],
    )
    speech_rate = forms.SliderField(
        TooltipLabel(_("speaking speed"), _("[-50,100], 100 means 2x speed, -50 means 0.5x speed")),
        required=True,
        default_value=0,
        _min=-50,
        _max=100,
        _step=1,
        precision=0,
    )
    loudness_rate = forms.SliderField(
        TooltipLabel(_("volume"), _("[-50,100], 100 means 2x volume, -50 means 0.5x volume")),
        required=True,
        default_value=0,
        _min=-50,
        _max=100,
        _step=1,
        precision=0,
    )


class VolcanicEngineTTSModelCredential(BaseForm, BaseModelCredential):
    api_url = forms.TextInputField(
        "API URL", required=True, default_value="https://openspeech.bytedance.com/api/v3/tts/unidirectional"
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
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get("value") == model_type, model_type_list))):
            raise AppApiException(
                ValidCode.valid_error.value,
                gettext("{model_type} Model type is not supported").format(model_type=model_type),
            )

        for key in ["api_url", "api_key"]:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, gettext("{key}  is required").format(key=key))
                else:
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
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, "api_key": super().encryption(model.get("api_key", ""))}

    def get_model_params_setting_form(self, model_name):
        return VolcanicEngineTTSModelGeneralParams()
