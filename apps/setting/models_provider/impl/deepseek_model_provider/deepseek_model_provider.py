#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：MaxKB 
@File    ：deepseek_model_provider.py
@Author  ：Brian Yang
@Date    ：5/12/24 7:40 AM 
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
from setting.models_provider.impl.deepseek_model_provider.model.deepseek_chat_model import DeepSeekChatModel
from smartdoc.conf import PROJECT_DIR


class DeepSeekLLMModelCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], raise_exception=False):
        model_type_list = DeepSeekModelProvider().get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')

        for key in ['api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            model = DeepSeekModelProvider().get_model(model_type, model_name, model_credential)
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


deepseek_llm_model_credential = DeepSeekLLMModelCredential()

model_dict = {
    'deepseek-chat': ModelInfo('deepseek-chat', '擅长通用对话任务，支持 32K 上下文', ModelTypeConst.LLM,
                               deepseek_llm_model_credential,
                               ),
    'deepseek-coder': ModelInfo('deepseek-coder', '擅长处理编程任务，支持 16K 上下文', ModelTypeConst.LLM,
                                deepseek_llm_model_credential,
                                ),
}


class DeepSeekModelProvider(IModelProvider):

    def get_dialogue_number(self):
        return 3

    def get_model(self, model_type, model_name, model_credential: Dict[str, object], **model_kwargs) -> DeepSeekChatModel:
        deepseek_chat_open_ai = DeepSeekChatModel(
            model=model_name,
            openai_api_base='https://api.deepseek.com',
            openai_api_key=model_credential.get('api_key')
        )
        return deepseek_chat_open_ai

    def get_model_credential(self, model_type, model_name):
        if model_name in model_dict:
            return model_dict.get(model_name).model_credential
        return deepseek_llm_model_credential

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_deepseek_provider', name='DeepSeek', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'deepseek_model_provider', 'icon',
                         'deepseek_icon_svg')))

    def get_model_list(self, model_type: str):
        if model_type is None:
            raise AppApiException(500, '模型类型不能为空')
        return [model_dict.get(key).to_dict() for key in
                list(filter(lambda key: model_dict.get(key).model_type == model_type, model_dict.keys()))]

    def get_model_type_list(self):
        return [{'key': "大语言模型", 'value': "LLM"}]
