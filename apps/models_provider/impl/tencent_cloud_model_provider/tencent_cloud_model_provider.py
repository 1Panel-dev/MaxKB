# coding=utf-8
"""
@project: maxkb
@Author：虎
@file： openai_model_provider.py
@date：2024/3/28 16:26
@desc:
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
from models_provider.impl.tencent_cloud_model_provider.credential.llm import TencentCloudLLMModelCredential
from models_provider.impl.tencent_cloud_model_provider.model.llm import TencentCloudChatModel
from maxkb.conf import PROJECT_DIR
from django.utils.translation import gettext_lazy as _

openai_llm_model_credential = TencentCloudLLMModelCredential()
model_info_list = [
    ModelInfo("deepseek-v3", "", ModelTypeConst.LLM, openai_llm_model_credential, TencentCloudChatModel),
    ModelInfo("deepseek-r1", "", ModelTypeConst.LLM, openai_llm_model_credential, TencentCloudChatModel),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_default_model_info(
        ModelInfo("deepseek-v3", "", ModelTypeConst.LLM, openai_llm_model_credential, TencentCloudChatModel)
    )
    .build()
)


class TencentCloudModelProvider(IModelProvider):
    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(
            provider="model_tencent_cloud_provider",
            name=_("Tencent Cloud"),
            icon=get_file_content(
                os.path.join(
                    PROJECT_DIR,
                    "apps",
                    "models_provider",
                    "impl",
                    "tencent_cloud_model_provider",
                    "icon",
                    "tencent_cloud_icon_svg",
                )
            ),
        )
