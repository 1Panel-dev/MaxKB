# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/10/16 17:01
    @desc:
"""
import traceback
from typing import Dict, Any

from django.utils.translation import gettext as _

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from models_provider.impl.aliyun_bai_lian_model_provider.model.embedding import AliyunBaiLianEmbedding

class BaiLianEmbeddingModelParams(BaseForm):
    dimensions = forms.SingleSelect(
        TooltipLabel(
            _('Dimensions'),
            _('')
        ),
        required=True,
        default_value=1024,
        value_field='value',
        text_field='label',
        option_list=[
            {'label': '1024', 'value': '1024'},
            {'label': '768', 'value': '768'},
            {'label': '512', 'value': '512'},
        ]
    )


class AliyunBaiLianEmbeddingCredential(BaseForm, BaseModelCredential):

    def is_valid(
            self,
            model_type: str,
            model_name: str,
            model_credential: Dict[str, Any],
            model_params: Dict[str, Any],
            provider: Any,
            raise_exception: bool = False
    ) -> bool:
        """
        验证模型凭据是否有效
        """
        model_type_list = provider.get_model_type_list()
        if not any(mt.get('value') == model_type for mt in model_type_list):
            raise AppApiException(
                ValidCode.valid_error.value,
                f"{model_type} Model type is not supported"
            )
        required_keys = ['dashscope_api_key']
        missing_keys = [key for key in required_keys if key not in model_credential]
        if missing_keys:
            if raise_exception:
                raise AppApiException(
                    ValidCode.valid_error.value,
                    f"{', '.join(missing_keys)} is required"
                )
            return False

        try:
            model: AliyunBaiLianEmbedding = provider.get_model(model_type, model_name, model_credential)
            model.embed_query(_("Hello"))
        except Exception as e:
            traceback.print_exc()
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(
                    ValidCode.valid_error.value,
                    f"Verification failed, please check whether the parameters are correct: {e}"
                )
            return False

        return True

    def encryption_dict(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """
        加密敏感信息
        """
        api_key = model.get('dashscope_api_key', '')
        return {**model, 'dashscope_api_key': super().encryption(api_key)}


    def get_model_params_setting_form(self, model_name):
        return BaiLianEmbeddingModelParams()

    dashscope_api_key = forms.PasswordInputField('API Key', required=True)
