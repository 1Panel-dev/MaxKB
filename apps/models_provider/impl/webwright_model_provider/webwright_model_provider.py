# coding=utf-8
"""
    @project: MaxKB
    @file: webwright_model_provider.py
    @desc: WebWright provider. WebWright serves an OpenAI-compatible chat
           completions API at https://webwright.ai/v1 with the Wren R1 model.
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
from models_provider.impl.webwright_model_provider.credential.llm import WebWrightLLMModelCredential
from models_provider.impl.webwright_model_provider.model.llm import WebWrightChatModel
from maxkb.conf import PROJECT_DIR

webwright_llm_model_credential = WebWrightLLMModelCredential()
webwright_llm_list = [
    ModelInfo('wren-r1', '', ModelTypeConst.LLM, webwright_llm_model_credential, WebWrightChatModel),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(webwright_llm_list)
    .append_default_model_info(webwright_llm_list[0])
    .build()
)


class WebWrightModelProvider(IModelProvider):
    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(
            provider='model_webwright_provider',
            name='WebWright',
            icon=get_file_content(
                os.path.join(
                    PROJECT_DIR,
                    "apps",
                    "models_provider",
                    "impl",
                    "webwright_model_provider",
                    "icon",
                    "webwright_icon_svg",
                )
            ),
        )
