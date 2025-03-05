import traceback
from typing import Dict

from django.utils.translation import gettext as _

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode
from setting.models_provider.impl.aws_bedrock_model_provider.model.embedding import BedrockEmbeddingModel


class BedrockEmbeddingCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(mt.get('value') == model_type for mt in model_type_list):
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value,
                                      _('{model_type} Model type is not supported').format(model_type=model_type))
            return False

        required_keys = ['region_name', 'access_key_id', 'secret_access_key']
        if not all(key in model_credential for key in required_keys):
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value,
                                      _('The following fields are required: {keys}').format(
                                          keys=", ".join(required_keys)))
            return False

        try:
            model: BedrockEmbeddingModel = provider.get_model(model_type, model_name, model_credential)
            aa = model.embed_query(_('Hello'))
            print(aa)
        except AppApiException:
            raise
        except Exception as e:
            traceback.print_exc()
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value,
                                      _('Verification failed, please check whether the parameters are correct: {error}').format(
                                          error=str(e)))
            return False

        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'secret_access_key': super().encryption(model.get('secret_access_key', ''))}

    region_name = forms.TextInputField('Region Name', required=True)
    access_key_id = forms.TextInputField('Access Key ID', required=True)
    secret_access_key = forms.PasswordInputField('Secret Access Key', required=True)
