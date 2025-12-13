import traceback
from typing import Dict

from django.utils.translation import gettext_lazy as _, gettext
from langchain_core.documents import Document

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from models_provider.base_model_provider import ValidCode, BaseModelCredential


class BedrockRerankerModelParams(BaseForm):
    top_n = forms.SliderField(TooltipLabel(_('Top N'),
                                          _('Number of top documents to return after reranking')),
                             required=True, default_value=3,
                             _min=1,
                             _max=20,
                             _step=1,
                             precision=0)


class BedrockRerankerCredential(BaseForm, BaseModelCredential):
    access_key_id = forms.PasswordInputField(_('Access Key ID'), required=True)
    secret_access_key = forms.PasswordInputField(_('Secret Access Key'), required=True)
    region_name = forms.TextInputField(_('Region Name'), required=True, default_value='us-east-1')
    base_url = forms.TextInputField(_('Base URL'), required=False)

    def is_valid(self, model_type: str, model_name: str, model_credential: Dict[str, object], model_params,
                 provider,
                 raise_exception: bool = False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, _('Model type is not supported'))

        for key in ['access_key_id', 'secret_access_key', 'region_name']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, _('%(key)s is required') % {'key': key})
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            # Use top_n=1 for validation since we only have 1 test document
            test_docs = [
                Document(page_content=str(_('Hello'))),
                Document(page_content=str(_('World'))),
                Document(page_content=str(_('Test')))
            ]
            model.compress_documents(test_docs, str(_('Hello')))
        except Exception as e:
            traceback.print_exc()
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value,
                                      _('Verification failed, please check whether the parameters are correct: %(error)s') % {'error': str(e)})
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'access_key_id': super().encryption(model.get('access_key_id', '')),
                'secret_access_key': super().encryption(model.get('secret_access_key', ''))}

    def get_model_params_setting_form(self, model_name):
        return BedrockRerankerModelParams()
