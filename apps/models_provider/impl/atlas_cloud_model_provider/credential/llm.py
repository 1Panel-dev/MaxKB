from typing import Dict

from django.utils.translation import gettext, gettext_lazy as _
from langchain_core.messages import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from models_provider.impl.atlas_cloud_model_provider.constants import ATLAS_CLOUD_API_BASE


class AtlasCloudLLMModelParams(BaseForm):
    temperature = forms.SliderField(
        TooltipLabel(
            _("Temperature"),
            _("Higher values make the output more random, while lower values make it more focused and deterministic"),
        ),
        required=True,
        default_value=0.7,
        _min=0.1,
        _max=1.0,
        _step=0.01,
        precision=2,
    )

    max_tokens = forms.SliderField(
        TooltipLabel(
            _("Output the maximum Tokens"),
            _("Specify the maximum number of tokens that the model can generate"),
        ),
        required=True,
        default_value=8192,
        _min=1,
        _max=100000,
        _step=1,
        precision=0,
    )


class AtlasCloudLLMModelCredential(BaseForm, BaseModelCredential):
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
        if not any(item.get("value") == model_type for item in model_type_list):
            raise AppApiException(
                ValidCode.valid_error.value,
                gettext("{model_type} Model type is not supported").format(model_type=model_type),
            )

        for key in ["api_base", "api_key"]:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(
                        ValidCode.valid_error.value,
                        gettext("{key}  is required").format(key=key),
                    )
                return False

        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            model.invoke([HumanMessage(content=gettext("Hello"))])
        except Exception as exc:
            maxkb_logger.error("Exception: %s", exc, exc_info=True)
            if isinstance(exc, AppApiException):
                raise exc
            if raise_exception:
                raise AppApiException(
                    ValidCode.valid_error.value,
                    gettext("Verification failed, please check whether the parameters are correct: {error}").format(
                        error=str(exc)
                    ),
                )
            return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, "api_key": super().encryption(model.get("api_key", ""))}

    api_base = forms.TextInputField(_("API URL"), required=True, default_value=ATLAS_CLOUD_API_BASE)
    api_key = forms.PasswordInputField("API Key", required=True)

    def get_model_params_setting_form(self, model_name):
        return AtlasCloudLLMModelParams()
