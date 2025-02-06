# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： xf_model_provider.py
    @date：2024/04/19 14:47
    @desc:
"""
import os
import ssl

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import ModelProvideInfo, ModelTypeConst, ModelInfo, IModelProvider, \
    ModelInfoManage
from setting.models_provider.impl.xf_model_provider.credential.embedding import XFEmbeddingCredential
from setting.models_provider.impl.xf_model_provider.credential.image import XunFeiImageModelCredential
from setting.models_provider.impl.xf_model_provider.credential.llm import XunFeiLLMModelCredential
from setting.models_provider.impl.xf_model_provider.credential.stt import XunFeiSTTModelCredential
from setting.models_provider.impl.xf_model_provider.credential.tts import XunFeiTTSModelCredential
from setting.models_provider.impl.xf_model_provider.model.embedding import XFEmbedding
from setting.models_provider.impl.xf_model_provider.model.image import XFSparkImage
from setting.models_provider.impl.xf_model_provider.model.llm import XFChatSparkLLM
from setting.models_provider.impl.xf_model_provider.model.stt import XFSparkSpeechToText
from setting.models_provider.impl.xf_model_provider.model.tts import XFSparkTextToSpeech
from smartdoc.conf import PROJECT_DIR
from django.utils.translation import gettext as _

ssl._create_default_https_context = ssl.create_default_context()

qwen_model_credential = XunFeiLLMModelCredential()
stt_model_credential = XunFeiSTTModelCredential()
image_model_credential = XunFeiImageModelCredential()
tts_model_credential = XunFeiTTSModelCredential()
embedding_model_credential = XFEmbeddingCredential()
model_info_list = [
    ModelInfo('generalv3.5', '', ModelTypeConst.LLM, qwen_model_credential, XFChatSparkLLM),
    ModelInfo('generalv3', '', ModelTypeConst.LLM, qwen_model_credential, XFChatSparkLLM),
    ModelInfo('generalv2', '', ModelTypeConst.LLM, qwen_model_credential, XFChatSparkLLM),
    ModelInfo('iat', _('Chinese and English recognition'), ModelTypeConst.STT, stt_model_credential, XFSparkSpeechToText),
    ModelInfo('tts', '', ModelTypeConst.TTS, tts_model_credential, XFSparkTextToSpeech),
    ModelInfo('embedding', '', ModelTypeConst.EMBEDDING, embedding_model_credential, XFEmbedding)
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_default_model_info(
        ModelInfo('generalv3.5', '', ModelTypeConst.LLM, qwen_model_credential, XFChatSparkLLM))
    .append_default_model_info(
        ModelInfo('iat', _('Chinese and English recognition'), ModelTypeConst.STT, stt_model_credential, XFSparkSpeechToText),
    )
    .append_default_model_info(
        ModelInfo('tts', '', ModelTypeConst.TTS, tts_model_credential, XFSparkTextToSpeech))
    .append_default_model_info(
        ModelInfo('embedding', '', ModelTypeConst.EMBEDDING, embedding_model_credential, XFEmbedding))
    .build()
)


class XunFeiModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_xf_provider', name=_('iFlytek Spark'), icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'xf_model_provider', 'icon',
                         'xf_icon_svg')))
