from typing import Dict

from langchain_core.documents import Document

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from django.utils.translation import gettext_lazy as _

from models_provider.impl.vllm_model_provider.model.reranker import VllmBgeReranker
from common.utils.logger import maxkb_logger

class VllmRerankerCredential(BaseForm, BaseModelCredential):
    api_url = forms.TextInputField('API URL', required=True)
    api_key = forms.PasswordInputField('API Key', required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=True):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  _('{model_type} Model type is not supported').format(model_type=model_type))

        for key in ['api_url', 'api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, _('{key}  is required').format(key=key))
                else:
                    return False
        try:
            model: VllmBgeReranker = provider.get_model(model_type, model_name, model_credential)
            test_text = str(_('Hello'))
            model.compress_documents([Document(page_content=test_text)], test_text)
        except Exception as e:
            maxkb_logger.error(f'Exception: {e}', exc_info=True)
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(
                    ValidCode.valid_error.value,
                    _('Verification failed, please check whether the parameters are correct: {error}').format(
                        error=str(e))
                )
            return False

        return True

    def encryption_dict(self, model_info: Dict[str, object]):
        return {**model_info, 'api_key': super().encryption(model_info.get('api_key', ''))}