#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：MaxKB
@File    ：orcarouter_model_provider.py
@Date    ：2026-08-15
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
from models_provider.impl.orcarouter_model_provider.credential.llm import OrcaRouterLLMModelCredential
from models_provider.impl.orcarouter_model_provider.model.llm import OrcaRouterChatModel
from maxkb.conf import PROJECT_DIR

orcarouter_llm_model_credential = OrcaRouterLLMModelCredential()
orcarouter_llm_list = [
    ModelInfo("orcarouter/auto", "", ModelTypeConst.LLM, orcarouter_llm_model_credential, OrcaRouterChatModel),
    ModelInfo("openai/gpt-5.5", "", ModelTypeConst.LLM, orcarouter_llm_model_credential, OrcaRouterChatModel),
    ModelInfo("google/gemini-3.5-flash", "", ModelTypeConst.LLM, orcarouter_llm_model_credential,
              OrcaRouterChatModel),
    ModelInfo("anthropic/claude-opus-4.8", "", ModelTypeConst.LLM, orcarouter_llm_model_credential,
              OrcaRouterChatModel),
    ModelInfo("grok/grok-4.3", "", ModelTypeConst.LLM, orcarouter_llm_model_credential, OrcaRouterChatModel),
    ModelInfo("deepseek/deepseek-v4-pro", "", ModelTypeConst.LLM, orcarouter_llm_model_credential,
              OrcaRouterChatModel),
    ModelInfo("minimax/minimax-m2.7", "", ModelTypeConst.LLM, orcarouter_llm_model_credential,
              OrcaRouterChatModel),
    ModelInfo("qwen/qwen3.7-max", "", ModelTypeConst.LLM, orcarouter_llm_model_credential, OrcaRouterChatModel),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(orcarouter_llm_list)
    .append_default_model_info(orcarouter_llm_list[1])
    .build()
)


class OrcaRouterModelProvider(IModelProvider):
    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(
            provider="model_orcarouter_provider",
            name="OrcaRouter",
            icon=get_file_content(
                os.path.join(
                    PROJECT_DIR,
                    "apps",
                    "models_provider",
                    "impl",
                    "orcarouter_model_provider",
                    "icon",
                    "orcarouter_icon_svg",
                )
            ),
        )
