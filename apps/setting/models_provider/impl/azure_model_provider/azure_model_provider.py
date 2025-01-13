# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： azure_model_provider.py
    @date：2023/10/31 16:19
    @desc:
"""
import os

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, \
    ModelTypeConst, ModelInfoManage
from setting.models_provider.impl.azure_model_provider.credential.embedding import AzureOpenAIEmbeddingCredential
from setting.models_provider.impl.azure_model_provider.credential.image import AzureOpenAIImageModelCredential
from setting.models_provider.impl.azure_model_provider.credential.llm import AzureLLMModelCredential
from setting.models_provider.impl.azure_model_provider.credential.stt import AzureOpenAISTTModelCredential
from setting.models_provider.impl.azure_model_provider.credential.tti import AzureOpenAITextToImageModelCredential
from setting.models_provider.impl.azure_model_provider.credential.tts import AzureOpenAITTSModelCredential
from setting.models_provider.impl.azure_model_provider.model.azure_chat_model import AzureChatModel
from setting.models_provider.impl.azure_model_provider.model.embedding import AzureOpenAIEmbeddingModel
from setting.models_provider.impl.azure_model_provider.model.image import AzureOpenAIImage
from setting.models_provider.impl.azure_model_provider.model.stt import AzureOpenAISpeechToText
from setting.models_provider.impl.azure_model_provider.model.tti import AzureOpenAITextToImage
from setting.models_provider.impl.azure_model_provider.model.tts import AzureOpenAITextToSpeech
from smartdoc.conf import PROJECT_DIR
from django.utils.translation import gettext_lazy as _

base_azure_llm_model_credential = AzureLLMModelCredential()
base_azure_embedding_model_credential = AzureOpenAIEmbeddingCredential()
base_azure_image_model_credential = AzureOpenAIImageModelCredential()
base_azure_tti_model_credential = AzureOpenAITextToImageModelCredential()
base_azure_tts_model_credential = AzureOpenAITTSModelCredential()
base_azure_stt_model_credential = AzureOpenAISTTModelCredential()

default_model_info = [
    ModelInfo('Azure OpenAI', '', ModelTypeConst.LLM,
              base_azure_llm_model_credential, AzureChatModel, api_version='2024-02-15-preview'
              ),
    ModelInfo('gpt-4', '', ModelTypeConst.LLM,
              base_azure_llm_model_credential, AzureChatModel, api_version='2024-02-15-preview'
              ),
    ModelInfo('gpt-4o', '', ModelTypeConst.LLM,
              base_azure_llm_model_credential, AzureChatModel, api_version='2024-02-15-preview'
              ),
    ModelInfo('gpt-4o-mini', '', ModelTypeConst.LLM,
              base_azure_llm_model_credential, AzureChatModel, api_version='2024-02-15-preview'
              ),
]

embedding_model_info = [
    ModelInfo('text-embedding-3-large', '', ModelTypeConst.EMBEDDING,
              base_azure_embedding_model_credential, AzureOpenAIEmbeddingModel, api_version='2023-05-15'
              ),
    ModelInfo('text-embedding-3-small', '', ModelTypeConst.EMBEDDING,
              base_azure_embedding_model_credential, AzureOpenAIEmbeddingModel, api_version='2023-05-15'
              ),
    ModelInfo('text-embedding-ada-002', '', ModelTypeConst.EMBEDDING,
              base_azure_embedding_model_credential, AzureOpenAIEmbeddingModel, api_version='2023-05-15'
              ),
]

image_model_info = [
    ModelInfo('gpt-4o', '', ModelTypeConst.IMAGE,
              base_azure_image_model_credential, AzureOpenAIImage, api_version='2023-05-15'
              ),
    ModelInfo('gpt-4o-mini', '', ModelTypeConst.IMAGE,
              base_azure_image_model_credential, AzureOpenAIImage, api_version='2023-05-15'
              ),
]

tti_model_info = [
    ModelInfo('dall-e-3', '', ModelTypeConst.TTI,
              base_azure_tti_model_credential, AzureOpenAITextToImage, api_version='2023-05-15'
              ),
]

tts_model_info = [
    ModelInfo('tts', '', ModelTypeConst.TTS,
              base_azure_tts_model_credential, AzureOpenAITextToSpeech, api_version='2023-05-15'
              ),
]

stt_model_info = [
    ModelInfo('whisper', '', ModelTypeConst.STT,
              base_azure_stt_model_credential, AzureOpenAISpeechToText, api_version='2023-05-15'
              ),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_default_model_info(default_model_info[0])
    .append_model_info_list(default_model_info)
    .append_model_info_list(embedding_model_info)
    .append_default_model_info(embedding_model_info[0])
    .append_model_info_list(image_model_info)
    .append_default_model_info(image_model_info[0])
    .append_model_info_list(stt_model_info)
    .append_default_model_info(stt_model_info[0])
    .append_model_info_list(tts_model_info)
    .append_default_model_info(tts_model_info[0])
    .append_model_info_list(tti_model_info)
    .append_default_model_info(tti_model_info[0])
    .build()
)


class AzureModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_azure_provider', name='Azure OpenAI', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'azure_model_provider', 'icon',
                         'azure_icon_svg')))
