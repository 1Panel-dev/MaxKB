#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：MaxKB
@File    ：deepseek_model_provider.py
@Author  ：Brian Yang
@Date    ：5/12/24 7:40 AM
"""

import os

from common.utils.common import get_file_content
from models_provider.base_model_provider import (
    IModelProvider,
    ModelProvideInfo,
    ModelInfo,
    ModelTypeConst,
    ModelInfoManage,
)
from models_provider.impl.deepseek_model_provider.credential.llm import DeepSeekLLMModelCredential
from models_provider.impl.deepseek_model_provider.model.llm import DeepSeekChatModel
from maxkb.conf import PROJECT_DIR

deepseek_llm_model_credential = DeepSeekLLMModelCredential()
deepseek_llm_list = [
    ModelInfo("deepseek-v4-pro", "", ModelTypeConst.LLM, deepseek_llm_model_credential, DeepSeekChatModel),
    ModelInfo("deepseek-v4-flash", "", ModelTypeConst.LLM, deepseek_llm_model_credential, DeepSeekChatModel),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(deepseek_llm_list)
    .append_default_model_info(deepseek_llm_list[0])
    .build()
)


class DeepSeekModelProvider(IModelProvider):
    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(
            provider="model_deepseek_provider",
            name="DeepSeek",
            icon=get_file_content(
                os.path.join(
                    PROJECT_DIR,
                    "apps",
                    "models_provider",
                    "impl",
                    "deepseek_model_provider",
                    "icon",
                    "deepseek_icon_svg",
                )
            ),
        )
