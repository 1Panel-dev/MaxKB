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
from models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, \
    ModelTypeConst, ModelInfoManage
from models_provider.impl.anthropic_model_provider.credential.image import AnthropicImageModelCredential
from models_provider.impl.anthropic_model_provider.credential.llm import AnthropicLLMModelCredential
from models_provider.impl.anthropic_model_provider.model.image import AnthropicImage
from models_provider.impl.anthropic_model_provider.model.llm import AnthropicChatModel
from maxkb.conf import PROJECT_DIR

openai_llm_model_credential = AnthropicLLMModelCredential()
openai_image_model_credential = AnthropicImageModelCredential()

# Claude model ids: https://platform.claude.com/docs/en/about-claude/models/overview
model_info_list = [
    ModelInfo('claude-opus-4-6', '', ModelTypeConst.LLM,
              openai_llm_model_credential, AnthropicChatModel
              ),
    ModelInfo('claude-sonnet-4-6', '', ModelTypeConst.LLM, openai_llm_model_credential,
              AnthropicChatModel),
    ModelInfo('claude-haiku-4-5-20251001', '', ModelTypeConst.LLM, openai_llm_model_credential,
              AnthropicChatModel),
]

image_model_info = [
    ModelInfo('claude-sonnet-4-6', '', ModelTypeConst.IMAGE, openai_image_model_credential,
              AnthropicImage),
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

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_anthropic_provider', name='Anthropic', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", 'models_provider', 'impl', 'anthropic_model_provider', 'icon',
                         'anthropic_icon_svg')))
