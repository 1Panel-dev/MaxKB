# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： web.py
    @date：2025/11/7 14:23
    @desc:
"""
from typing import Dict

import requests
from django.utils.translation import gettext_lazy as _

from common import forms
from common.forms import BaseForm
from maxkb.const import CONFIG
from models_provider.base_model_provider import BaseModelCredential


class LocalRerankerCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        bind = f'{CONFIG.get("LOCAL_MODEL_HOST")}:{CONFIG.get("LOCAL_MODEL_PORT")}'
        prefix = CONFIG.get_admin_path()
        res = requests.post(
            f'{CONFIG.get("LOCAL_MODEL_PROTOCOL")}://{bind}{prefix}/api/model/validate',
            json={'model_name': model_name, 'model_type': model_type, 'model_credential': model_credential})
        result = res.json()
        if result.get('code', 500) == 200:
            return result.get('data')
        raise Exception(result.get('message'))

    def encryption_dict(self, model: Dict[str, object]):
        return model

    cache_folder = forms.TextInputField(_('Model catalog'), required=True)
