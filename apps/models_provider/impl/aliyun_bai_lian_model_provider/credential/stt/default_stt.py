# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： default_stt.py
    @date：2025/12/5 15:12
    @desc:
"""
from typing import Dict, Any

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from maxkb.settings import maxkb_logger
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from django.utils.translation import gettext as _



class AliyunBaiLianDefaultSTTModelCredential(BaseForm, BaseModelCredential):
    type = forms.Radio(_("Type"), required=True, text_field='label', default_value='qwen', provider='', method='',
                       value_field='value', option_list=[
            {'label': _('Audio file recognition - Tongyi Qwen'),
             'value': 'qwen'},
            {'label': _('Qwen-Omni'),
             'value': 'omni'},
            {'label': _('Audio file recognition - Fun-ASR/Paraformer/SenseVoice'),
             'value': 'other'}
        ])
    api_url = forms.TextInputField(_('API URL'), required=True, relation_show_field_dict={'type': ['qwen', 'omni']})
    api_key = forms.PasswordInputField(_('API Key'), required=True)

    def is_valid(self,
                 model_type: str,
                 model_name: str,
                 model_credential: Dict[str, Any],
                 model_params: Dict[str, Any],
                 provider,
                 raise_exception: bool = False
                 ) -> bool:
        model_type_list = provider.get_model_type_list()
        model_type_list = provider.get_model_type_list()
        if not any(mt.get('value') == model_type for mt in model_type_list):
            raise AppApiException(
                ValidCode.valid_error.value,
                _('{model_type} Model type is not supported').format(model_type=model_type)
            )

        required_keys = ['api_key']
        for key in required_keys:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(
                        ValidCode.valid_error.value,
                        _('{key} is required').format(key=key)
                    )
                return False

        try:
            model = provider.get_model(model_type, model_name, model_credential)
            model.check_auth()
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

    def encryption_dict(self, model: Dict[str, object]) -> Dict[str, object]:

        return {
            **model,
            'api_key': super().encryption(model.get('api_key', ''))
        }

    def get_model_params_setting_form(self, model_name):

        pass