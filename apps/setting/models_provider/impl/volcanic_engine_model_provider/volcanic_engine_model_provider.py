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
from setting.models_provider.impl.openai_model_provider.credential.llm import OpenAILLMModelCredential
from setting.models_provider.impl.volcanic_engine_model_provider.credential.embedding import VolcanicEmbeddingCredential
from setting.models_provider.impl.volcanic_engine_model_provider.credential.image import \
    VolcanicEngineImageModelCredential
from setting.models_provider.impl.volcanic_engine_model_provider.credential.tti import VolcanicEngineTTIModelCredential
from setting.models_provider.impl.volcanic_engine_model_provider.credential.tts import VolcanicEngineTTSModelCredential
from setting.models_provider.impl.volcanic_engine_model_provider.model.embedding import VolcanicEngineEmbeddingModel
from setting.models_provider.impl.volcanic_engine_model_provider.model.image import VolcanicEngineImage
from setting.models_provider.impl.volcanic_engine_model_provider.model.llm import VolcanicEngineChatModel
from setting.models_provider.impl.volcanic_engine_model_provider.credential.stt import VolcanicEngineSTTModelCredential
from setting.models_provider.impl.volcanic_engine_model_provider.model.stt import VolcanicEngineSpeechToText
from setting.models_provider.impl.volcanic_engine_model_provider.model.tti import VolcanicEngineTextToImage
from setting.models_provider.impl.volcanic_engine_model_provider.model.tts import VolcanicEngineTextToSpeech

from smartdoc.conf import PROJECT_DIR
from django.utils.translation import gettext as _

volcanic_engine_llm_model_credential = OpenAILLMModelCredential()
volcanic_engine_stt_model_credential = VolcanicEngineSTTModelCredential()
volcanic_engine_tts_model_credential = VolcanicEngineTTSModelCredential()
volcanic_engine_image_model_credential = VolcanicEngineImageModelCredential()
volcanic_engine_tti_model_credential = VolcanicEngineTTIModelCredential()

model_info_list = [
    ModelInfo('ep-xxxxxxxxxx-yyyy',
              _('The user goes to the model inference page of Volcano Ark to create an inference access point. Here, you need to enter ep-xxxxxxxxxx-yyyy to call it.'),
              ModelTypeConst.LLM,
              volcanic_engine_llm_model_credential, VolcanicEngineChatModel
              ),
    ModelInfo('ep-xxxxxxxxxx-yyyy',
              _('The user goes to the model inference page of Volcano Ark to create an inference access point. Here, you need to enter ep-xxxxxxxxxx-yyyy to call it.'),
              ModelTypeConst.IMAGE,
              volcanic_engine_image_model_credential, VolcanicEngineImage
              ),
    ModelInfo('asr',
              '',
              ModelTypeConst.STT,
              volcanic_engine_stt_model_credential, VolcanicEngineSpeechToText
              ),
    ModelInfo('tts',
              '',
              ModelTypeConst.TTS,
              volcanic_engine_tts_model_credential, VolcanicEngineTextToSpeech
              ),
    ModelInfo('general_v2.0',
              _('Universal 2.0-Vincent Diagram'),
              ModelTypeConst.TTI,
              volcanic_engine_tti_model_credential, VolcanicEngineTextToImage
              ),
    ModelInfo('general_v2.0_L',
              _('Universal 2.0Pro-Vincent Chart'),
              ModelTypeConst.TTI,
              volcanic_engine_tti_model_credential, VolcanicEngineTextToImage
              ),
    ModelInfo('general_v1.4',
              _('Universal 1.4-Vincent Chart'),
              ModelTypeConst.TTI,
              volcanic_engine_tti_model_credential, VolcanicEngineTextToImage
              ),
    ModelInfo('anime_v1.3',
              _('Animation 1.3.0-Vincent Picture'),
              ModelTypeConst.TTI,
              volcanic_engine_tti_model_credential, VolcanicEngineTextToImage
              ),
    ModelInfo('anime_v1.3.1',
              _('Animation 1.3.1-Vincent Picture'),
              ModelTypeConst.TTI,
              volcanic_engine_tti_model_credential, VolcanicEngineTextToImage
              ),
]

open_ai_embedding_credential = VolcanicEmbeddingCredential()
model_info_embedding_list = [
    ModelInfo('ep-xxxxxxxxxx-yyyy',
              _('The user goes to the model inference page of Volcano Ark to create an inference access point. Here, you need to enter ep-xxxxxxxxxx-yyyy to call it.'),
              ModelTypeConst.EMBEDDING, open_ai_embedding_credential,
              VolcanicEngineEmbeddingModel)
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_default_model_info(model_info_list[0])
    .append_default_model_info(model_info_list[1])
    .append_default_model_info(model_info_list[2])
    .append_default_model_info(model_info_list[3])
    .append_default_model_info(model_info_list[4])
    .append_model_info_list(model_info_embedding_list)
    .append_default_model_info(model_info_embedding_list[0])
    .build()
)


class VolcanicEngineModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_volcanic_engine_provider', name=_('volcano engine'), icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'volcanic_engine_model_provider',
                         'icon',
                         'volcanic_engine_icon_svg')))
