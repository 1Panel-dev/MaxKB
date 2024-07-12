#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：MaxKB 
@File    ：deepseek_model_provider.py
@Author  ：Brian Yang
@Date    ：5/12/24 7:40 AM 
"""
import os

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, ModelTypeConst, \
    ModelInfoManage
from setting.models_provider.impl.deepseek_model_provider.credential.llm import DeepSeekLLMModelCredential
from setting.models_provider.impl.deepseek_model_provider.model.llm import DeepSeekChatModel
from smartdoc.conf import PROJECT_DIR

deepseek_llm_model_credential = DeepSeekLLMModelCredential()

deepseek_chat = ModelInfo('deepseek-chat', '擅长通用对话任务，支持 32K 上下文', ModelTypeConst.LLM,
                          deepseek_llm_model_credential, DeepSeekChatModel
                          )

deepseek_coder = ModelInfo('deepseek-coder', '擅长处理编程任务，支持 16K 上下文', ModelTypeConst.LLM,
                           deepseek_llm_model_credential,
                           DeepSeekChatModel)

model_info_manage = ModelInfoManage.builder().append_model_info(deepseek_chat).append_model_info(
    deepseek_coder).append_default_model_info(
    deepseek_coder).build()


class DeepSeekModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_deepseek_provider', name='DeepSeek', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'deepseek_model_provider', 'icon',
                         'deepseek_icon_svg')))
