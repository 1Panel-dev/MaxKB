#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：MaxKB 
@File    ：gemini_model_provider.py
@Author  ：Brian Yang
@Date    ：5/13/24 7:47 AM 
"""
import os

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, ModelTypeConst, \
    ModelInfoManage
from setting.models_provider.impl.gemini_model_provider.credential.embedding import GeminiEmbeddingCredential
from setting.models_provider.impl.gemini_model_provider.credential.image import GeminiImageModelCredential
from setting.models_provider.impl.gemini_model_provider.credential.llm import GeminiLLMModelCredential
from setting.models_provider.impl.gemini_model_provider.credential.stt import GeminiSTTModelCredential
from setting.models_provider.impl.gemini_model_provider.model.embedding import GeminiEmbeddingModel
from setting.models_provider.impl.gemini_model_provider.model.image import GeminiImage
from setting.models_provider.impl.gemini_model_provider.model.llm import GeminiChatModel
from setting.models_provider.impl.gemini_model_provider.model.stt import GeminiSpeechToText
from smartdoc.conf import PROJECT_DIR
from django.utils.translation import gettext as _


gemini_llm_model_credential = GeminiLLMModelCredential()
gemini_image_model_credential = GeminiImageModelCredential()
gemini_stt_model_credential = GeminiSTTModelCredential()
gemini_embedding_model_credential = GeminiEmbeddingCredential()

model_info_list = [
    ModelInfo('gemini-1.0-pro', _('Latest Gemini 1.0 Pro model, updated with Google update'),
              ModelTypeConst.LLM,
              gemini_llm_model_credential,
              GeminiChatModel),
    ModelInfo('gemini-1.0-pro-vision', _('Latest Gemini 1.0 Pro Vision model, updated with Google update'),
              ModelTypeConst.LLM,
              gemini_llm_model_credential,
              GeminiChatModel),
]

model_image_info_list = [
    ModelInfo('gemini-1.5-flash', _('Latest Gemini 1.5 Flash model, updated with Google updates'),
              ModelTypeConst.IMAGE,
              gemini_image_model_credential,
              GeminiImage),
    ModelInfo('gemini-1.5-pro', _('Latest Gemini 1.5 Flash model, updated with Google updates'),
              ModelTypeConst.IMAGE,
              gemini_image_model_credential,
              GeminiImage),
]

model_stt_info_list = [
    ModelInfo('gemini-1.5-flash', _('Latest Gemini 1.5 Flash model, updated with Google updates'),
              ModelTypeConst.STT,
              gemini_stt_model_credential,
              GeminiSpeechToText),
    ModelInfo('gemini-1.5-pro', _('Latest Gemini 1.5 Flash model, updated with Google updates'),
              ModelTypeConst.STT,
              gemini_stt_model_credential,
              GeminiSpeechToText),
]

model_embedding_info_list = [
    ModelInfo('models/embedding-001', '',
              ModelTypeConst.EMBEDDING,
              gemini_embedding_model_credential,
              GeminiEmbeddingModel),
    ModelInfo('models/text-embedding-004', '',
              ModelTypeConst.EMBEDDING,
              gemini_embedding_model_credential,
              GeminiEmbeddingModel),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_model_info_list(model_image_info_list)
    .append_model_info_list(model_stt_info_list)
    .append_model_info_list(model_embedding_info_list)
    .append_default_model_info(model_info_list[0])
    .append_default_model_info(model_image_info_list[0])
    .append_default_model_info(model_stt_info_list[0])
    .append_default_model_info(model_embedding_info_list[0])
    .build()
)


class GeminiModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_gemini_provider', name='Gemini', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'gemini_model_provider', 'icon',
                         'gemini_icon_svg')))
