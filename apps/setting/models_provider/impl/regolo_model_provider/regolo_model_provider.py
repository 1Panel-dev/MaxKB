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
from setting.models_provider.impl.regolo_model_provider.credential.embedding import \
    RegoloEmbeddingCredential
from setting.models_provider.impl.regolo_model_provider.credential.llm import RegoloLLMModelCredential
from setting.models_provider.impl.regolo_model_provider.credential.tti import \
    RegoloTextToImageModelCredential
from setting.models_provider.impl.regolo_model_provider.model.embedding import RegoloEmbeddingModel
from setting.models_provider.impl.regolo_model_provider.model.llm import RegoloChatModel
from setting.models_provider.impl.regolo_model_provider.model.tti import RegoloTextToImage
from smartdoc.conf import PROJECT_DIR
from django.utils.translation import gettext as _

openai_llm_model_credential = RegoloLLMModelCredential()
openai_tti_model_credential = RegoloTextToImageModelCredential()
model_info_list = [
    ModelInfo('Phi-4', '', ModelTypeConst.LLM,
              openai_llm_model_credential, RegoloChatModel
              ),
    ModelInfo('DeepSeek-R1-Distill-Qwen-32B', '', ModelTypeConst.LLM,
              openai_llm_model_credential,
              RegoloChatModel),
    ModelInfo('maestrale-chat-v0.4-beta', '',
              ModelTypeConst.LLM, openai_llm_model_credential,
              RegoloChatModel),
    ModelInfo('Llama-3.3-70B-Instruct',
              '',
              ModelTypeConst.LLM, openai_llm_model_credential,
              RegoloChatModel),
    ModelInfo('Llama-3.1-8B-Instruct',
              '',
              ModelTypeConst.LLM, openai_llm_model_credential,
              RegoloChatModel),
    ModelInfo('DeepSeek-Coder-6.7B-Instruct', '',
              ModelTypeConst.LLM, openai_llm_model_credential,
              RegoloChatModel)
]
open_ai_embedding_credential = RegoloEmbeddingCredential()
model_info_embedding_list = [
    ModelInfo('gte-Qwen2', '',
              ModelTypeConst.EMBEDDING, open_ai_embedding_credential,
              RegoloEmbeddingModel),
]

model_info_tti_list = [
    ModelInfo('FLUX.1-dev', '',
              ModelTypeConst.TTI, openai_tti_model_credential,
              RegoloTextToImage),
    ModelInfo('sdxl-turbo', '',
              ModelTypeConst.TTI, openai_tti_model_credential,
              RegoloTextToImage),
]
model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_default_model_info(
        ModelInfo('gpt-3.5-turbo', _('The latest gpt-3.5-turbo, updated with OpenAI adjustments'), ModelTypeConst.LLM,
                  openai_llm_model_credential, RegoloChatModel
                  ))
    .append_model_info_list(model_info_embedding_list)
    .append_default_model_info(model_info_embedding_list[0])
    .append_model_info_list(model_info_tti_list)
    .append_default_model_info(model_info_tti_list[0])

    .build()
)


class RegoloModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_regolo_provider', name='Regolo', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'regolo_model_provider',
                         'icon',
                         'regolo_icon_svg')))
