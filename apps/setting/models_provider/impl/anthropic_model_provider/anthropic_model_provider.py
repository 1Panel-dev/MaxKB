# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： openai_model_provider.py
    @date：2024/3/28 16:26
    @desc:
"""
import os

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, \
    ModelTypeConst, ModelInfoManage
from setting.models_provider.impl.anthropic_model_provider.credential.image import AnthropicImageModelCredential
from setting.models_provider.impl.anthropic_model_provider.credential.llm import AnthropicLLMModelCredential
from setting.models_provider.impl.anthropic_model_provider.model.image import AnthropicImage
from setting.models_provider.impl.anthropic_model_provider.model.llm import AnthropicChatModel
from smartdoc.conf import PROJECT_DIR

openai_llm_model_credential = AnthropicLLMModelCredential()
openai_image_model_credential = AnthropicImageModelCredential()

model_info_list = [
    ModelInfo('claude-3-opus-20240229', '', ModelTypeConst.LLM,
              openai_llm_model_credential, AnthropicChatModel
              ),
    ModelInfo('claude-3-sonnet-20240229', '', ModelTypeConst.LLM, openai_llm_model_credential,
              AnthropicChatModel),
    ModelInfo('claude-3-haiku-20240307', '', ModelTypeConst.LLM, openai_llm_model_credential,
              AnthropicChatModel),
    ModelInfo('claude-3-5-sonnet-20240620', '', ModelTypeConst.LLM, openai_llm_model_credential,
              AnthropicChatModel),
    ModelInfo('claude-3-5-haiku-20241022', '', ModelTypeConst.LLM, openai_llm_model_credential,
              AnthropicChatModel),
    ModelInfo('claude-3-5-sonnet-20241022', '', ModelTypeConst.LLM, openai_llm_model_credential,
              AnthropicChatModel),
]

image_model_info = [
    ModelInfo('claude-3-5-sonnet-20241022', '', ModelTypeConst.IMAGE, openai_image_model_credential,
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
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'anthropic_model_provider', 'icon',
                         'anthropic_icon_svg')))
