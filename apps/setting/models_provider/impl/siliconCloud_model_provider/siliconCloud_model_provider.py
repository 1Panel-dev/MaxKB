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
from setting.models_provider.impl.siliconCloud_model_provider.credential.embedding import \
    SiliconCloudEmbeddingCredential
from setting.models_provider.impl.siliconCloud_model_provider.credential.llm import SiliconCloudLLMModelCredential
from setting.models_provider.impl.siliconCloud_model_provider.credential.reranker import SiliconCloudRerankerCredential
from setting.models_provider.impl.siliconCloud_model_provider.credential.stt import SiliconCloudSTTModelCredential
from setting.models_provider.impl.siliconCloud_model_provider.credential.tti import \
    SiliconCloudTextToImageModelCredential
from setting.models_provider.impl.siliconCloud_model_provider.model.embedding import SiliconCloudEmbeddingModel
from setting.models_provider.impl.siliconCloud_model_provider.model.llm import SiliconCloudChatModel
from setting.models_provider.impl.siliconCloud_model_provider.model.reranker import SiliconCloudReranker
from setting.models_provider.impl.siliconCloud_model_provider.model.stt import SiliconCloudSpeechToText
from setting.models_provider.impl.siliconCloud_model_provider.model.tti import SiliconCloudTextToImage
from smartdoc.conf import PROJECT_DIR
from django.utils.translation import gettext as _

openai_llm_model_credential = SiliconCloudLLMModelCredential()
openai_stt_model_credential = SiliconCloudSTTModelCredential()
openai_reranker_model_credential = SiliconCloudRerankerCredential()
openai_tti_model_credential = SiliconCloudTextToImageModelCredential()
model_info_list = [
    ModelInfo('deepseek-ai/DeepSeek-R1-Distill-Llama-8B', '', ModelTypeConst.LLM,
              openai_llm_model_credential, SiliconCloudChatModel
              ),
    ModelInfo('deepseek-ai/DeepSeek-R1-Distill-Qwen-7B', '', ModelTypeConst.LLM,
              openai_llm_model_credential,
              SiliconCloudChatModel),
    ModelInfo('deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B', '',
              ModelTypeConst.LLM, openai_llm_model_credential,
              SiliconCloudChatModel),
    ModelInfo('Qwen/Qwen2.5-7B-Instruct',
              '',
              ModelTypeConst.LLM, openai_llm_model_credential,
              SiliconCloudChatModel),
    ModelInfo('Qwen/Qwen2.5-Coder-7B-Instruct', '',
              ModelTypeConst.LLM, openai_llm_model_credential,
              SiliconCloudChatModel),
    ModelInfo('internlm/internlm2_5-7b-chat', '',
              ModelTypeConst.LLM, openai_llm_model_credential,
              SiliconCloudChatModel),
    ModelInfo('Qwen/Qwen2-1.5B-Instruct', '',
              ModelTypeConst.LLM, openai_llm_model_credential,
              SiliconCloudChatModel),
    ModelInfo('THUDM/glm-4-9b-chat', '',
              ModelTypeConst.LLM, openai_llm_model_credential,
              SiliconCloudChatModel),
    ModelInfo('FunAudioLLM/SenseVoiceSmall', '',
              ModelTypeConst.STT, openai_stt_model_credential,
              SiliconCloudSpeechToText),
]
open_ai_embedding_credential = SiliconCloudEmbeddingCredential()
model_info_embedding_list = [
    ModelInfo('netease-youdao/bce-embedding-base_v1', '',
              ModelTypeConst.EMBEDDING, open_ai_embedding_credential,
              SiliconCloudEmbeddingModel),
    ModelInfo('BAAI/bge-m3', '',
              ModelTypeConst.EMBEDDING, open_ai_embedding_credential,
              SiliconCloudEmbeddingModel),
    ModelInfo('BAAI/bge-large-en-v1.5', '',
              ModelTypeConst.EMBEDDING, open_ai_embedding_credential,
              SiliconCloudEmbeddingModel),
    ModelInfo('BAAI/bge-large-zh-v1.5', '',
              ModelTypeConst.EMBEDDING, open_ai_embedding_credential,
              SiliconCloudEmbeddingModel),
]

model_info_tti_list = [
    ModelInfo('deepseek-ai/Janus-Pro-7B', '',
              ModelTypeConst.TTI, openai_tti_model_credential,
              SiliconCloudTextToImage),
    ModelInfo('stabilityai/stable-diffusion-3-5-large', '',
              ModelTypeConst.TTI, openai_tti_model_credential,
              SiliconCloudTextToImage),
    ModelInfo('black-forest-labs/FLUX.1-schnell', '',
              ModelTypeConst.TTI, openai_tti_model_credential,
              SiliconCloudTextToImage),
    ModelInfo('stabilityai/stable-diffusion-3-medium', '',
              ModelTypeConst.TTI, openai_tti_model_credential,
              SiliconCloudTextToImage),
    ModelInfo('stabilityai/stable-diffusion-xl-base-1.0', '',
              ModelTypeConst.TTI, openai_tti_model_credential,
              SiliconCloudTextToImage),
    ModelInfo('stabilityai/stable-diffusion-2-1', '',
              ModelTypeConst.TTI, openai_tti_model_credential,
              SiliconCloudTextToImage),
]
model_rerank_list = [
    ModelInfo('netease-youdao/bce-reranker-base_v1', '', ModelTypeConst.RERANKER,
              openai_reranker_model_credential, SiliconCloudReranker
              ),
    ModelInfo('BAAI/bge-reranker-v2-m3', '', ModelTypeConst.RERANKER,
              openai_reranker_model_credential, SiliconCloudReranker
              ),
]
model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_default_model_info(
        ModelInfo('gpt-3.5-turbo', _('The latest gpt-3.5-turbo, updated with OpenAI adjustments'), ModelTypeConst.LLM,
                  openai_llm_model_credential, SiliconCloudChatModel
                  ))
    .append_model_info_list(model_info_embedding_list)
    .append_default_model_info(model_info_embedding_list[0])
    .append_model_info_list(model_info_tti_list)
    .append_default_model_info(model_info_tti_list[0])
    .append_default_model_info(ModelInfo('whisper-1', '',
                                         ModelTypeConst.STT, openai_stt_model_credential,
                                         SiliconCloudSpeechToText))
    .append_model_info_list(model_rerank_list)
    .append_default_model_info(model_rerank_list[0])

    .build()
)


class SiliconCloudModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_siliconCloud_provider', name='SILICONFLOW', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'siliconCloud_model_provider',
                         'icon',
                         'siliconCloud_icon_svg')))
