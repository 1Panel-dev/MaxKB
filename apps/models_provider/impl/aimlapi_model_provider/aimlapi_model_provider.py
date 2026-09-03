# coding=utf-8
"""
    @project: MaxKB
    @Author：aimlapi.com
    @file： aimlapi_model_provider.py
    @date：2026/09/03 10:00
    @desc:
"""
import os

from common.utils.common import get_file_content
from maxkb.conf import PROJECT_DIR
from models_provider.base_model_provider import ModelInfo, ModelTypeConst, ModelInfoManage, IModelProvider, \
    ModelProvideInfo
from models_provider.impl.aimlapi_model_provider.credential.embedding import AIMLAPIEmbeddingCredential
from models_provider.impl.aimlapi_model_provider.credential.image import AIMLAPIImageModelCredential
from models_provider.impl.aimlapi_model_provider.credential.llm import AIMLAPILLMModelCredential
from models_provider.impl.aimlapi_model_provider.credential.tti import AIMLAPITextToImageModelCredential
from models_provider.impl.aimlapi_model_provider.model.embedding import AIMLAPIEmbeddingModel
from models_provider.impl.aimlapi_model_provider.model.image import AIMLAPIImage
from models_provider.impl.aimlapi_model_provider.model.llm import AIMLAPIChatModel
from models_provider.impl.aimlapi_model_provider.model.tti import AIMLAPITextToImage

aimlapi_llm_model_credential = AIMLAPILLMModelCredential()
aimlapi_image_model_credential = AIMLAPIImageModelCredential()
aimlapi_embedding_model_credential = AIMLAPIEmbeddingCredential()
aimlapi_tti_model_credential = AIMLAPITextToImageModelCredential()

# AI/ML API 提供 350 多个对话模型，这里只列出常用的一部分，
# 其余模型可以在添加模型时直接填写模型名称。
# 模型 ID 以 https://api.aimlapi.com/v1/models 为准，注意点号写法（如 claude-sonnet-4.5）。
model_info_list = [
    ModelInfo('openai/gpt-5-5', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel),
    ModelInfo('openai/gpt-5-mini', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel),
    ModelInfo('openai/gpt-4.1', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel),
    ModelInfo('openai/gpt-4.1-mini', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel),
    ModelInfo('openai/gpt-4o', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel),
    ModelInfo('openai/gpt-4o-mini', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel),
    ModelInfo('anthropic/claude-opus-4.5', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel),
    ModelInfo('anthropic/claude-sonnet-4.5', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel),
    ModelInfo('anthropic/claude-haiku-4.5', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel),
    ModelInfo('google/gemini-2.5-pro', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel),
    ModelInfo('google/gemini-2.5-flash', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel),
    ModelInfo('deepseek/deepseek-v4-flash', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel),
    ModelInfo('alibaba/qwen3-max', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel),
    ModelInfo('zhipu/glm-4.6', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel),
    ModelInfo('moonshotai/kimi-k2', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel),
    ModelInfo('meta-llama/Llama-3.3-70B-Instruct-Turbo', '', ModelTypeConst.LLM, aimlapi_llm_model_credential,
              AIMLAPIChatModel),
    ModelInfo('mistralai/mistral-medium-3.1', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel),
    ModelInfo('x-ai/grok-4-6', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel),
]

model_info_image_list = [
    ModelInfo('openai/gpt-4o', '', ModelTypeConst.IMAGE, aimlapi_image_model_credential, AIMLAPIImage),
    ModelInfo('openai/gpt-4o-mini', '', ModelTypeConst.IMAGE, aimlapi_image_model_credential, AIMLAPIImage),
    ModelInfo('openai/gpt-4.1', '', ModelTypeConst.IMAGE, aimlapi_image_model_credential, AIMLAPIImage),
    ModelInfo('google/gemini-2.5-pro', '', ModelTypeConst.IMAGE, aimlapi_image_model_credential, AIMLAPIImage),
    ModelInfo('google/gemini-2.5-flash', '', ModelTypeConst.IMAGE, aimlapi_image_model_credential, AIMLAPIImage),
    ModelInfo('anthropic/claude-sonnet-4.5', '', ModelTypeConst.IMAGE, aimlapi_image_model_credential, AIMLAPIImage),
    ModelInfo('alibaba/qwen3-vl-plus', '', ModelTypeConst.IMAGE, aimlapi_image_model_credential, AIMLAPIImage),
]

model_info_embedding_list = [
    ModelInfo('openai/text-embedding-3-small', '', ModelTypeConst.EMBEDDING, aimlapi_embedding_model_credential,
              AIMLAPIEmbeddingModel),
    ModelInfo('openai/text-embedding-3-large', '', ModelTypeConst.EMBEDDING, aimlapi_embedding_model_credential,
              AIMLAPIEmbeddingModel),
    ModelInfo('openai/text-embedding-ada-002', '', ModelTypeConst.EMBEDDING, aimlapi_embedding_model_credential,
              AIMLAPIEmbeddingModel),
    ModelInfo('alibaba/text-embedding-v4', '', ModelTypeConst.EMBEDDING, aimlapi_embedding_model_credential,
              AIMLAPIEmbeddingModel),
    ModelInfo('google/text-multilingual-embedding-002', '', ModelTypeConst.EMBEDDING,
              aimlapi_embedding_model_credential, AIMLAPIEmbeddingModel),
    ModelInfo('anthropic/voyage-multilingual-2', '', ModelTypeConst.EMBEDDING, aimlapi_embedding_model_credential,
              AIMLAPIEmbeddingModel),
]

model_info_tti_list = [
    ModelInfo('flux/schnell', '', ModelTypeConst.TTI, aimlapi_tti_model_credential, AIMLAPITextToImage),
    ModelInfo('google/gemini-2.5-flash-image', '', ModelTypeConst.TTI, aimlapi_tti_model_credential,
              AIMLAPITextToImage),
    ModelInfo('openai/gpt-image-1', '', ModelTypeConst.TTI, aimlapi_tti_model_credential, AIMLAPITextToImage),
    ModelInfo('alibaba/qwen-image', '', ModelTypeConst.TTI, aimlapi_tti_model_credential, AIMLAPITextToImage),
    ModelInfo('bytedance/seedream-v4-text-to-image', '', ModelTypeConst.TTI, aimlapi_tti_model_credential,
              AIMLAPITextToImage),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_default_model_info(
        ModelInfo('openai/gpt-4o-mini', '', ModelTypeConst.LLM, aimlapi_llm_model_credential, AIMLAPIChatModel))
    .append_model_info_list(model_info_image_list)
    .append_default_model_info(model_info_image_list[0])
    .append_model_info_list(model_info_embedding_list)
    .append_default_model_info(model_info_embedding_list[0])
    .append_model_info_list(model_info_tti_list)
    .append_default_model_info(model_info_tti_list[0])
    .build()
)


class AIMLAPIModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_aimlapi_provider', name='aimlapi.com', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", 'models_provider', 'impl', 'aimlapi_model_provider', 'icon',
                         'aimlapi_icon_svg')))
