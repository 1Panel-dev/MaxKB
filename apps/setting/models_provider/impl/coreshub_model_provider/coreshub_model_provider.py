# coding=utf-8
"""
    @project: maxkb
    @Author：Qingyang
    @file： coreshub_model_provider.py
    @date：2025/2/11 12:11
    @desc:
"""
import os

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, \
    ModelTypeConst, ModelInfoManage
from setting.models_provider.impl.coreshub_model_provider.credential.embedding import CoresHubEmbeddingCredential
from setting.models_provider.impl.coreshub_model_provider.credential.llm import CoresHubLLMModelCredential
from setting.models_provider.impl.coreshub_model_provider.model.llm import CoresHubChatModel
from setting.models_provider.impl.coreshub_model_provider.model.embedding import CoresHubEmbeddingModel
from setting.models_provider.impl.coreshub_model_provider.credential.tts import CoresHubTTSModelCredential
from setting.models_provider.impl.coreshub_model_provider.credential.stt import CoresHubSTTModelCredential
from setting.models_provider.impl.coreshub_model_provider.model.stt import CoresHubSpeechToText
from setting.models_provider.impl.coreshub_model_provider.model.tts import CoresHubTextToSpeech
from smartdoc.conf import PROJECT_DIR
from django.utils.translation import gettext as _

coreshub_llm_model_credential = CoresHubLLMModelCredential()
model_info_list = [
    ModelInfo('DeepSeek-V3', '', ModelTypeConst.LLM,
              coreshub_llm_model_credential, CoresHubChatModel
              ),
    ModelInfo('DeepSeek-R1', '', ModelTypeConst.LLM,
              coreshub_llm_model_credential,
              CoresHubChatModel),
    ModelInfo('DeepSeek-R1-Distill-Llama-70B', '',
              ModelTypeConst.LLM, coreshub_llm_model_credential,
              CoresHubChatModel),
    ModelInfo('DeepSeek-R1-Distill-Qwen-32B',
              '',
              ModelTypeConst.LLM, coreshub_llm_model_credential,
              CoresHubChatModel),
    ModelInfo('DeepSeek-R1-Distill-Llama-70B', '',
              ModelTypeConst.LLM, coreshub_llm_model_credential,
              CoresHubChatModel),
    ModelInfo('DeepSeek-R1-Distill-Qwen-14B', '',
              ModelTypeConst.LLM, coreshub_llm_model_credential,
              CoresHubChatModel),
    ModelInfo('DeepSeek-R1-Distill-Llama-8B', '',
              ModelTypeConst.LLM, coreshub_llm_model_credential,
              CoresHubChatModel),
    ModelInfo('DeepSeek-R1-Distill-Qwen-7B', '',
              ModelTypeConst.LLM, coreshub_llm_model_credential,
              CoresHubChatModel),
    ModelInfo('DeepSeek-R1-Distill-Qwen-1.5B', '',
              ModelTypeConst.LLM, coreshub_llm_model_credential,
              CoresHubChatModel),
    ModelInfo('Qwen2-0.5B-Instruct', '',
              ModelTypeConst.LLM, coreshub_llm_model_credential,
              CoresHubChatModel)
]

coreshub_embedding_credential = CoresHubEmbeddingCredential()
model_info_embedding_list = [
    ModelInfo('bce-embedding-base_v1', '',
              ModelTypeConst.EMBEDDING, coreshub_embedding_credential,
              CoresHubEmbeddingModel)
]

coreshub_stt_model_credential = CoresHubSTTModelCredential()
model_info_stt_list = [
    ModelInfo('SenseVoiceSmall', '',
              ModelTypeConst.STT, coreshub_stt_model_credential,
              CoresHubSpeechToText)
]

coreshub_tts_model_credential = CoresHubTTSModelCredential()
model_info_tts_list = [
    ModelInfo('CosyVoice-300M', '',
              ModelTypeConst.TTS, coreshub_tts_model_credential,
              CoresHubTextToSpeech)
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_default_model_info(model_info_list[0])
    .append_model_info_list(model_info_embedding_list)
    .append_default_model_info(model_info_embedding_list[0])
    .append_model_info_list(model_info_stt_list)
    .append_default_model_info(model_info_stt_list[0])
    .append_model_info_list(model_info_tts_list)
    .append_default_model_info(model_info_tts_list[0])
    .build()
)


class CoresHubModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_coreshub_provider', name='CoresHub', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'coreshub_model_provider', 'icon',
                         'coreshub_icon_svg')))
