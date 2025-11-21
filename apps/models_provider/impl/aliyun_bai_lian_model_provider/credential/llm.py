# coding=utf-8
from typing import Dict

from langchain_core.messages import HumanMessage
from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from common.utils.logger import maxkb_logger

class BaiLianLLMModelParams(BaseForm):
    temperature = forms.SliderField(
        TooltipLabel(
            _('Temperature'),
            _('Higher values make the output more random, while lower values make it more focused and deterministic')
        ),
        required=True,
        default_value=0.7,
        _min=0.1,
        _max=1.0,
        _step=0.01,
        precision=2
    )

    max_tokens = forms.SliderField(
        TooltipLabel(
            _('Output the maximum Tokens'),
            _('Specify the maximum number of tokens that the model can generate.')
        ),
        required=True,
        default_value=800,
        _min=1,
        _max=100000,
        _step=1,
        precision=0
    )


class BaiLianLLMModelCredential(BaseForm, BaseModelCredential):
    api_base = forms.TextInputField(_('API URL'), required=True)
    api_key = forms.PasswordInputField(_('API Key'), required=True)

    def is_valid(
            self,
            model_type: str,
            model_name: str,
            model_credential: Dict[str, object],
            model_params: dict,
            provider,
            raise_exception: bool = False
    ) -> bool:
        model_type_list = provider.get_model_type_list()
        if not any(mt.get('value') == model_type for mt in model_type_list):
            raise AppApiException(
                ValidCode.valid_error.value,
                gettext('{model_type} Model type is not supported').format(model_type=model_type)
            )

        for key in ['api_base', 'api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(
                        ValidCode.valid_error.value,
                        gettext('{key} is required').format(key=key)
                    )
                return False

        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            if model_params.get('stream'):
                for res in model.stream([HumanMessage(content=gettext('Hello'))]):
                    pass
            else:
                model.invoke([HumanMessage(content=gettext('Hello'))])
        except Exception as e:
            maxkb_logger.error(f'Exception: {e}', exc_info=True)
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(
                    ValidCode.valid_error.value,
                    gettext('Verification failed, please check whether the parameters are correct: {error}').format(
                        error=str(e)
                    )
                )
            return False

        return True

    def encryption_dict(self, model: Dict[str, object]) -> Dict[str, object]:
        return {**model, 'api_key': super().encryption(model.get('api_key', ''))}

    def get_model_params_setting_form(self, model_name: str) -> BaiLianLLMModelParams:
        return BaiLianLLMModelParams()
