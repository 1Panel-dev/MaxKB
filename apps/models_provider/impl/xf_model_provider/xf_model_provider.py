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

from common.utils.common import get_file_content
from models_provider.base_model_provider import ModelProvideInfo, ModelTypeConst, ModelInfo, IModelProvider, \
    ModelInfoManage
from models_provider.impl.xf_model_provider.credential.embedding import XFEmbeddingCredential
from models_provider.impl.xf_model_provider.credential.image import XunFeiImageModelCredential
from models_provider.impl.xf_model_provider.credential.llm import XunFeiLLMModelCredential
from models_provider.impl.xf_model_provider.credential.stt import XunFeiSTTModelCredential
from models_provider.impl.xf_model_provider.credential.tts import XunFeiTTSModelCredential
from models_provider.impl.xf_model_provider.credential.super_humanoid_tts import XunFeiSuperHumanoidTTSModelCredential
from models_provider.impl.xf_model_provider.credential.default_tts import XunFeiDefaultTTSModelCredential
from models_provider.impl.xf_model_provider.credential.zh_en_stt import ZhEnXunFeiSTTModelCredential
from models_provider.impl.xf_model_provider.model.embedding import XFEmbedding
from models_provider.impl.xf_model_provider.model.image import XFSparkImage
from models_provider.impl.xf_model_provider.model.llm import XFChatSparkLLM
from models_provider.impl.xf_model_provider.model.stt import XFSparkSpeechToText
from models_provider.impl.xf_model_provider.model.tts import XFSparkTextToSpeech
from models_provider.impl.xf_model_provider.model.super_humanoid_tts import XFSparkSuperHumanoidTextToSpeech
from models_provider.impl.xf_model_provider.model.default_tts import XFSparkDefaultTextToSpeech
from maxkb.conf import PROJECT_DIR
from django.utils.translation import gettext as _

from models_provider.impl.xf_model_provider.model.zh_en_stt import XFZhEnSparkSpeechToText

ssl._create_default_https_context = ssl.create_default_context()

xunfei_model_credential = XunFeiLLMModelCredential()
stt_model_credential = XunFeiSTTModelCredential()
zh_en_stt_credential = ZhEnXunFeiSTTModelCredential()
image_model_credential = XunFeiImageModelCredential()
# TTS credentials
tts_model_credential = XunFeiTTSModelCredential()
super_humanoid_tts_credential = XunFeiSuperHumanoidTTSModelCredential()
default_tts_credential = XunFeiDefaultTTSModelCredential()
embedding_model_credential = XFEmbeddingCredential()

model_info_list = [
    ModelInfo('generalv3.5', '', ModelTypeConst.LLM, xunfei_model_credential, XFChatSparkLLM),
    ModelInfo('generalv3', '', ModelTypeConst.LLM, xunfei_model_credential, XFChatSparkLLM),
    ModelInfo('generalv2', '', ModelTypeConst.LLM, xunfei_model_credential, XFChatSparkLLM),
    ModelInfo('iat', _('Chinese and English recognition'), ModelTypeConst.STT, stt_model_credential,
              XFSparkSpeechToText),
    ModelInfo('slm', _('Chinese and English recognition'), ModelTypeConst.STT, zh_en_stt_credential,
              XFZhEnSparkSpeechToText),
    # 具体 TTS 模型
    ModelInfo('tts', _('Online TTS'), ModelTypeConst.TTS, tts_model_credential, XFSparkTextToSpeech),
    ModelInfo('tts-super-humanoid', _('Super Humanoid TTS'), ModelTypeConst.TTS, super_humanoid_tts_credential,
              XFSparkSuperHumanoidTextToSpeech),
    ModelInfo('embedding', '', ModelTypeConst.EMBEDDING, embedding_model_credential, XFEmbedding)
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_default_model_info(
        ModelInfo('generalv3.5', '', ModelTypeConst.LLM, xunfei_model_credential, XFChatSparkLLM))
    .append_default_model_info(
        ModelInfo('iat', _('Chinese and English recognition'), ModelTypeConst.STT, stt_model_credential,
                  XFSparkSpeechToText),
    )
    # default TTS 工厂入口
    .append_default_model_info(
        ModelInfo('default', _('default'), ModelTypeConst.TTS, default_tts_credential, XFSparkDefaultTextToSpeech))
    .append_default_model_info(
        ModelInfo('embedding', '', ModelTypeConst.EMBEDDING, embedding_model_credential, XFEmbedding))
    .build()
)


class XunFeiModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_xf_provider', name=_('iFlytek Spark'), icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", 'models_provider', 'impl', 'xf_model_provider', 'icon',
                         'xf_icon_svg')))