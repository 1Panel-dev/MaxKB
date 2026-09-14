# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： llm.py
@date：2024/7/12 10:19
@desc:
"""

from typing import Dict

from django.utils.translation import gettext, gettext_lazy as _
from langchain_core.messages import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import BaseModelCredential, ValidCode


class QianfanLLMModelParams(BaseForm):
    temperature = forms.SliderField(
        TooltipLabel(
            _("Temperature"),
            _("Higher values make the output more random, while lower values make it more focused and deterministic"),
        ),
        required=True,
        default_value=0.95,
        _min=0.1,
        _max=1.0,
        _step=0.01,
        precision=2,
    )

    max_tokens = forms.SliderField(
        TooltipLabel(
            _("Output the maximum Tokens"), _("Specify the maximum number of tokens that the model can generate")
        ),
        required=True,
        default_value=1024,
        _min=2,
        _max=100000,
        _step=1,
        precision=0,
    )


class QianfanLLMModelCredential(BaseForm, BaseModelCredential):
    api_base = forms.TextInputField("API URL", required=True, default_value="https://qianfan.baidubce.com/v2")
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
            model = provider.get_model(model_type, model_name, model_credential, **{**model_params, "max_tokens": 1})
            model.invoke([HumanMessage(content="1")])
        except Exception as e:
            maxkb_logger.error(f"Exception: {e}", exc_info=True)
            raise e
        return True

    def encryption_dict(self, model_info: Dict[str, object]):
        return {**model_info, "api_key": super().encryption(model_info.get("api_key", ""))}

    def build_model(self, model_info: Dict[str, object]):
        for key in ["api_base", "api_key", "model"]:
            if key not in model_info:
                raise AppApiException(500, gettext("{key}  is required").format(key=key))
        self.api_base = model_info.get("api_base")
        self.api_key = model_info.get("api_key")
        return self

    def get_model_params_setting_form(self, model_name):
        return QianfanLLMModelParams()
