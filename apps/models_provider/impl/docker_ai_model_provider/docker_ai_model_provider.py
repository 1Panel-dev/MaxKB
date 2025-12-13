# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： docker_ai_model_provider.py
    @date：2024/3/28 16:26
    @desc:
"""
import os

from common.utils.common import get_file_content
from models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, \
    ModelTypeConst, ModelInfoManage
from models_provider.impl.docker_ai_model_provider.credential.embedding import DockerAIEmbeddingCredential
from models_provider.impl.docker_ai_model_provider.credential.image import DockerAIImageModelCredential
from models_provider.impl.docker_ai_model_provider.credential.llm import DockerAILLMModelCredential
from models_provider.impl.docker_ai_model_provider.credential.reranker import DockerAIRerankerCredential
from models_provider.impl.docker_ai_model_provider.credential.stt import DockerAISTTModelCredential
from models_provider.impl.docker_ai_model_provider.credential.tti import DockerAITextToImageModelCredential
from models_provider.impl.docker_ai_model_provider.credential.tts import DockerAITTSModelCredential
from models_provider.impl.docker_ai_model_provider.model.embedding import DockerAIEmbeddingModel
from models_provider.impl.docker_ai_model_provider.model.image import DockerAIImage
from models_provider.impl.docker_ai_model_provider.model.llm import DockerAIChatModel
from models_provider.impl.docker_ai_model_provider.model.reranker import DockerAIReranker
from models_provider.impl.docker_ai_model_provider.model.stt import DockerAISpeechToText
from models_provider.impl.docker_ai_model_provider.model.tti import DockerAITextToImage
from models_provider.impl.docker_ai_model_provider.model.tts import DockerAITextToSpeech
from maxkb.conf import PROJECT_DIR
from django.utils.translation import gettext_lazy as _

docker_ai_llm_model_credential = DockerAILLMModelCredential()
docker_ai_stt_model_credential = DockerAISTTModelCredential()
docker_ai_tts_model_credential = DockerAITTSModelCredential()
docker_ai_image_model_credential = DockerAIImageModelCredential()
docker_ai_tti_model_credential = DockerAITextToImageModelCredential()
model_info_list = [
    ModelInfo('ai/qwen3-vl:8B', '', ModelTypeConst.LLM,
              docker_ai_llm_model_credential, DockerAIChatModel
              ),
]
open_ai_embedding_credential = DockerAIEmbeddingCredential()
model_info_embedding_list = [
    ModelInfo('ai/qwen3-embedding-vllm', '',
              ModelTypeConst.EMBEDDING, open_ai_embedding_credential,
              DockerAIEmbeddingModel),
]

# model_info_image_list = [
#     ModelInfo('gpt-4o', _('The latest GPT-4o, cheaper and faster than gpt-4-turbo, updated with DockerAI adjustments'),
#               ModelTypeConst.IMAGE, docker_ai_image_model_credential,
#               DockerAIImage),
#     ModelInfo('gpt-4o-mini',
#               _('The latest gpt-4o-mini, cheaper and faster than gpt-4o, updated with DockerAI adjustments'),
#               ModelTypeConst.IMAGE, docker_ai_image_model_credential,
#               DockerAIImage),
# ]

# model_info_tti_list = [
#     ModelInfo('dall-e-3', '',
#               ModelTypeConst.TTI, docker_ai_tti_model_credential,
#               DockerAITextToImage),
# ]
docker_ai_reranker_model_credential = DockerAIRerankerCredential()
model_info_rerank_list = [
    ModelInfo('ai/qwen3-reranker:0.6B', '',
              ModelTypeConst.RERANKER, docker_ai_reranker_model_credential,
              DockerAIReranker),
]
model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_default_model_info(
        ModelInfo('gpt-3.5-turbo', _('The latest gpt-3.5-turbo, updated with DockerAI adjustments'), ModelTypeConst.LLM,
                  docker_ai_llm_model_credential, DockerAIChatModel
                  ))
    .append_model_info_list(model_info_embedding_list)
    .append_default_model_info(model_info_embedding_list[0])
    # .append_model_info_list(model_info_image_list)
    # .append_default_model_info(model_info_image_list[0])
    # .append_model_info_list(model_info_tti_list)
    # .append_default_model_info(model_info_tti_list[0])
    # .append_default_model_info(ModelInfo('whisper-1', '',
    #                                      ModelTypeConst.STT, docker_ai_stt_model_credential,
    #                                      DockerAISpeechToText)
    #                            )
    # .append_default_model_info(ModelInfo('tts-1', '',
    #                                      ModelTypeConst.TTS, docker_ai_tts_model_credential,
    #                                      DockerAITextToSpeech))
    .append_model_info_list(model_info_rerank_list)
    .append_default_model_info(model_info_rerank_list[0])
    .build()
)


class DockerModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_docker_ai_provider', name='Docker AI', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", 'models_provider', 'impl', 'docker_ai_model_provider', 'icon',
                         'docker_ai_icon_svg')))
