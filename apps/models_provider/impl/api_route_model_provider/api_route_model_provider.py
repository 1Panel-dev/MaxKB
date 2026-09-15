# coding=utf-8
"""
    @project: MaxKB
    @file: api_route_model_provider.py
    @desc: API Route Model Provider
"""
import os

from django.utils.translation import gettext as _

from common.utils.common import get_file_content
from maxkb.conf import PROJECT_DIR
from models_provider.base_model_provider import ModelInfo, ModelTypeConst, ModelInfoManage, IModelProvider, \
    ModelProvideInfo
from models_provider.impl.api_route_model_provider.credential.embedding import ApiRouteEmbeddingCredential
from models_provider.impl.api_route_model_provider.credential.llm import ApiRouteLLMModelCredential
from models_provider.impl.api_route_model_provider.model.embedding import ApiRouteEmbeddingModel
from models_provider.impl.api_route_model_provider.model.llm import ApiRouteChatModel

api_route_llm_credential = ApiRouteLLMModelCredential()
api_route_embedding_credential = ApiRouteEmbeddingCredential()

model_info_list = [
    ModelInfo('gpt-4o', '', ModelTypeConst.LLM,
              api_route_llm_credential, ApiRouteChatModel),
    ModelInfo('gpt-4o-mini', '', ModelTypeConst.LLM,
              api_route_llm_credential, ApiRouteChatModel),
    ModelInfo('claude-3-5-sonnet-20241022', '', ModelTypeConst.LLM,
              api_route_llm_credential, ApiRouteChatModel),
    ModelInfo('deepseek-chat', '', ModelTypeConst.LLM,
              api_route_llm_credential, ApiRouteChatModel),
    ModelInfo('deepseek-reasoner', '', ModelTypeConst.LLM,
              api_route_llm_credential, ApiRouteChatModel),
    ModelInfo('qwen-2.5-72b-instruct', '', ModelTypeConst.LLM,
              api_route_llm_credential, ApiRouteChatModel),
]

model_info_embedding_list = [
    ModelInfo('text-embedding-3-small', '',
              ModelTypeConst.EMBEDDING, api_route_embedding_credential,
              ApiRouteEmbeddingModel),
    ModelInfo('text-embedding-3-large', '',
              ModelTypeConst.EMBEDDING, api_route_embedding_credential,
              ApiRouteEmbeddingModel),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_default_model_info(
        ModelInfo('gpt-4o', _('OpenAI GPT-4o via API Route'), ModelTypeConst.LLM,
                  api_route_llm_credential, ApiRouteChatModel))
    .append_model_info_list(model_info_embedding_list)
    .append_default_model_info(model_info_embedding_list[0])
    .build()
)


class ApiRouteModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(
            provider='model_api_route_provider',
            name='API Route',
            icon=get_file_content(
                os.path.join(PROJECT_DIR, "apps", 'models_provider', 'impl', 'api_route_model_provider',
                             'icon',
                             'api_route_icon_svg'))
        )
