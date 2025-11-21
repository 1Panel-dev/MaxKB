# coding=utf-8

from typing import Dict, Any

from django.utils.translation import gettext as _
from langchain_core.documents import Document

from common.exception.app_exception import AppApiException
from common.forms import BaseForm, PasswordInputField
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from models_provider.impl.aliyun_bai_lian_model_provider.model.reranker import AliyunBaiLianReranker
from common.utils.logger import maxkb_logger

class AliyunBaiLianRerankerCredential(BaseForm, BaseModelCredential):
    """
    Credential class for the Aliyun BaiLian Reranker model.
    Provides validation and encryption for the model credentials.
    """

    dashscope_api_key = PasswordInputField('API Key', required=True)

    def is_valid(
        self,
        model_type: str,
        model_name: str,
        model_credential: Dict[str, Any],
        model_params: Dict[str, Any],
        provider,
        raise_exception: bool = False
    ) -> bool:
        """
        Validate the model credentials.

        :param model_type: Type of the model (e.g., 'RERANKER').
        :param model_name: Name of the model.
        :param model_credential: Dictionary containing the model credentials.
        :param model_params: Parameters for the model.
        :param provider: Model provider instance.
        :param raise_exception: Whether to raise an exception on validation failure.
        :return: Boolean indicating whether the credentials are valid.
        """
        if model_type != 'RERANKER':
            raise AppApiException(
                ValidCode.valid_error.value,
                _('{model_type} Model type is not supported').format(model_type=model_type)
            )

        required_keys = ['dashscope_api_key']
        for key in required_keys:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(
                        ValidCode.valid_error.value,
                        _('{key} is required').format(key=key)
                    )
                return False

        try:
            model: AliyunBaiLianReranker = provider.get_model(model_type, model_name, model_credential)
            model.compress_documents([Document(page_content=_('Hello'))], _('Hello'))
        except Exception as e:
            maxkb_logger.error(f'Exception: {e}', exc_info=True)
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(
                    ValidCode.valid_error.value,
                    _('Verification failed, please check whether the parameters are correct: {error}').format(error=str(e))
                )
            return False

        return True

    def encryption_dict(self, model: Dict[str, object]) -> Dict[str, object]:
        """
        Encrypt sensitive fields in the model dictionary.

        :param model: Dictionary containing model details.
        :return: Dictionary with encrypted sensitive fields.
        """
        return {
            **model,
            'dashscope_api_key': super().encryption(model.get('dashscope_api_key', ''))
        }
