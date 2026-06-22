#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：MaxKB
@File    ：atlascloud_model_provider.py
@desc    ：Atlas Cloud model provider (OpenAI-compatible MaaS gateway)
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
from models_provider.impl.atlascloud_model_provider.credential.llm import AtlasCloudLLMModelCredential
from models_provider.impl.atlascloud_model_provider.model.llm import AtlasCloudChatModel
from maxkb.conf import PROJECT_DIR

atlascloud_llm_model_credential = AtlasCloudLLMModelCredential()
atlascloud_llm_list = [
    ModelInfo("deepseek-ai/deepseek-v4-pro", "", ModelTypeConst.LLM, atlascloud_llm_model_credential,
              AtlasCloudChatModel),
    ModelInfo("qwen/qwen3-235b-a22b", "", ModelTypeConst.LLM, atlascloud_llm_model_credential,
              AtlasCloudChatModel),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(atlascloud_llm_list)
    .append_default_model_info(atlascloud_llm_list[0])
    .build()
)


class AtlasCloudModelProvider(IModelProvider):
    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(
            provider="model_atlascloud_provider",
            name="Atlas Cloud",
            icon=get_file_content(
                os.path.join(
                    PROJECT_DIR,
                    "apps",
                    "models_provider",
                    "impl",
                    "atlascloud_model_provider",
                    "icon",
                    "atlascloud_icon_svg",
                )
            ),
        )
