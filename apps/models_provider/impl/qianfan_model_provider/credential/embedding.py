# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： embedding.py
@date：2024/10/17 15:40
@desc:
"""

from typing import Dict

from django.utils.translation import gettext as _

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import BaseModelCredential, ValidCode


class QianfanEmbeddingCredential(BaseForm, BaseModelCredential):
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
                    raise AppApiException(ValidCode.valid_error.value, _("{key}  is required").format(key=key))
                return False

        try:
            model = provider.get_model(model_type, model_name, model_credential)
            model.embed_query(_("Hello"))
        except Exception as e:
            maxkb_logger.error(f"Exception: {e}", exc_info=True)
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(
                    ValidCode.valid_error.value,
                    _("Verification failed, please check whether the parameters are correct: {error}").format(
                        error=str(e)
                    ),
                )
            return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, "api_key": super().encryption(model.get("api_key", ""))}
