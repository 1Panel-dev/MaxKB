# coding=utf-8

from typing import Dict

from django.utils.translation import gettext as _

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from common.utils.logger import maxkb_logger


class TencentEmbeddingCredential(BaseForm, BaseModelCredential):
    def is_valid(
        self, model_type, model_name, model_credential: Dict[str, object], model_params, provider, raise_exception=True
    ):
        model_type_list = provider.get_model_type_list()
        if not any(mt.get("value") == model_type for mt in model_type_list):
            raise AppApiException(
                ValidCode.valid_error.value, _("{model_type} Model type is not supported").format(model_type=model_type)
            )

        if "api_key" not in model_credential:
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, _("api_key is required"))
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
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, "api_key": super().encryption(model.get("api_key", ""))}

    base_url = forms.TextInputField(
        label=TooltipLabel(_("API URL"), _("TokenHub OpenAI compatible embeddings endpoint")),
        required=False,
        default_value="https://tokenhub.tencentmaas.com/v1",
    )
    api_key = forms.PasswordInputField(_("API Key"), required=True)
