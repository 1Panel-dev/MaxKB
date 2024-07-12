#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：MaxKB 
@File    ：gemini_model_provider.py
@Author  ：Brian Yang
@Date    ：5/13/24 7:47 AM 
"""
import os

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, ModelTypeConst, \
    ModelInfoManage
from setting.models_provider.impl.gemini_model_provider.credential.llm import GeminiLLMModelCredential
from setting.models_provider.impl.gemini_model_provider.model.llm import GeminiChatModel
from smartdoc.conf import PROJECT_DIR

gemini_llm_model_credential = GeminiLLMModelCredential()

gemini_1_pro = ModelInfo('gemini-1.0-pro', '最新的Gemini 1.0 Pro模型，随Google更新而更新',
                         ModelTypeConst.LLM,
                         gemini_llm_model_credential,
                         GeminiChatModel)

gemini_1_pro_vision = ModelInfo('gemini-1.0-pro-vision', '最新的Gemini 1.0 Pro Vision模型，随Google更新而更新',
                                ModelTypeConst.LLM,
                                gemini_llm_model_credential,
                                GeminiChatModel)

model_info_manage = ModelInfoManage.builder().append_model_info(gemini_1_pro).append_model_info(
    gemini_1_pro_vision).append_default_model_info(gemini_1_pro).build()


class GeminiModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_gemini_provider', name='Gemini', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'gemini_model_provider', 'icon',
                         'gemini_icon_svg')))
