# coding=utf-8
"""
@project: maxkb
@Author：虎
@file： openai_model_provider.py
@date：2024/3/28 16:26
@desc:
"""

import os

import requests

from common.utils.common import get_file_content
from models_provider.base_model_provider import (
    IModelProvider,
    ModelProvideInfo,
    ModelInfo,
    ModelTypeConst,
    ModelInfoManage,
)
from models_provider.impl.anthropic_model_provider.credential.image import AnthropicImageModelCredential
from models_provider.impl.anthropic_model_provider.credential.llm import AnthropicLLMModelCredential
from models_provider.impl.anthropic_model_provider.model.image import AnthropicImage
from models_provider.impl.anthropic_model_provider.model.llm import AnthropicChatModel
from maxkb.conf import PROJECT_DIR

openai_llm_model_credential = AnthropicLLMModelCredential()
openai_image_model_credential = AnthropicImageModelCredential()

model_info_list = [
    ModelInfo("claude-3-opus-20240229", "", ModelTypeConst.LLM, openai_llm_model_credential, AnthropicChatModel),
    ModelInfo("claude-3-sonnet-20240229", "", ModelTypeConst.LLM, openai_llm_model_credential, AnthropicChatModel),
    ModelInfo("claude-3-haiku-20240307", "", ModelTypeConst.LLM, openai_llm_model_credential, AnthropicChatModel),
    ModelInfo("claude-3-5-sonnet-20240620", "", ModelTypeConst.LLM, openai_llm_model_credential, AnthropicChatModel),
    ModelInfo("claude-3-5-haiku-20241022", "", ModelTypeConst.LLM, openai_llm_model_credential, AnthropicChatModel),
    ModelInfo("claude-3-5-sonnet-20241022", "", ModelTypeConst.LLM, openai_llm_model_credential, AnthropicChatModel),
]

image_model_info = [
    ModelInfo("claude-3-5-sonnet-20241022", "", ModelTypeConst.IMAGE, openai_image_model_credential, AnthropicImage),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_default_model_info(model_info_list[0])
    .append_model_info_list(image_model_info)
    .append_default_model_info(image_model_info[0])
    .build()
)


class AnthropicModelProvider(IModelProvider):
    # Anthropic 凭证表单无 api_base 字段，实时查询使用官方默认地址。
    dynamic_default_api_base = "https://api.anthropic.com/v1"

    def fetch_dynamic_model_items(self, api_key, api_base, credential=None):
        """Anthropic 专有协议：GET {base}/v1/models，鉴权用 x-api-key 头。"""
        api_base = (api_base or self.get_dynamic_default_api_base() or "").strip().rstrip("/")
        if not api_base:
            return []
        url = api_base + ("/models" if api_base.endswith("/v1") else "/v1/models")
        try:
            response = requests.get(
                url,
                headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
                timeout=15,
            )
            if response.status_code != 200:
                return []
            data = response.json().get("data") or []
            return [item for item in data if item.get("id")]
        except Exception:
            return []

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(
            provider="model_anthropic_provider",
            name="Anthropic",
            icon=get_file_content(
                os.path.join(
                    PROJECT_DIR,
                    "apps",
                    "models_provider",
                    "impl",
                    "anthropic_model_provider",
                    "icon",
                    "anthropic_icon_svg",
                )
            ),
        )
