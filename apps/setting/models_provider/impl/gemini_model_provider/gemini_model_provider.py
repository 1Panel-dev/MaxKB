#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：MaxKB 
@File    ：gemini_model_provider.py
@Author  ：Brian Yang
@Date    ：5/13/24 7:47 AM 
"""
import os
from typing import Dict

from langchain.schema import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, BaseModelCredential, \
    ModelInfo, ModelTypeConst, ValidCode
from setting.models_provider.impl.gemini_model_provider.model.gemini_chat_model import GeminiChatModel
from smartdoc.conf import PROJECT_DIR


class GeminiLLMModelCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], raise_exception=False):
        model_type_list = GeminiModelProvider().get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')

        for key in ['api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            model = GeminiModelProvider().get_model(model_type, model_name, model_credential)
            model.invoke([HumanMessage(content='你好')])
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'校验失败,请检查参数是否正确: {str(e)}')
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'api_key': super().encryption(model.get('api_key', ''))}

    api_key = forms.PasswordInputField('API Key', required=True)


gemini_llm_model_credential = GeminiLLMModelCredential()

model_dict = {
    'gemini-1.0-pro': ModelInfo('gemini-1.0-pro', '最新的Gemini 1.0 Pro模型，随Google更新而更新',
                                ModelTypeConst.LLM,
                                gemini_llm_model_credential,
                                ),
    'gemini-1.0-pro-vision': ModelInfo('gemini-1.0-pro-vision', '最新的Gemini 1.0 Pro Vision模型，随Google更新而更新',
                                       ModelTypeConst.LLM,
                                       gemini_llm_model_credential,
                                       ),
}


class GeminiModelProvider(IModelProvider):

    def get_dialogue_number(self):
        return 3

    def get_model(self, model_type, model_name, model_credential: Dict[str, object],
                  **model_kwargs) -> GeminiChatModel:
        gemini_chat = GeminiChatModel(
            model=model_name,
            google_api_key=model_credential.get('api_key')
        )
        return gemini_chat

    def get_model_credential(self, model_type, model_name):
        if model_name in model_dict:
            return model_dict.get(model_name).model_credential
        return gemini_llm_model_credential

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_gemini_provider', name='Gemini', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'gemini_model_provider', 'icon',
                         'gemini_icon_svg')))

    def get_model_list(self, model_type: str):
        if model_type is None:
            raise AppApiException(500, '模型类型不能为空')
        return [model_dict.get(key).to_dict() for key in
                list(filter(lambda key: model_dict.get(key).model_type == model_type, model_dict.keys()))]

    def get_model_type_list(self):
        return [{'key': "大语言模型", 'value': "LLM"}]
