# coding=utf-8
import os

from common.utils.common import get_file_content
from models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, ModelTypeConst, \
    ModelInfoManage
from models_provider.impl.minimax_model_provider.credential.llm import MiniMaxLLMModelCredential
from models_provider.impl.minimax_model_provider.credential.tts import MiniMaxTTSModelCredential
from models_provider.impl.minimax_model_provider.model.llm import MiniMaxChatModel
from models_provider.impl.minimax_model_provider.model.tts import MiniMaxTextToSpeech
from maxkb.conf import PROJECT_DIR
from django.utils.translation import gettext_lazy as _

minimax_llm_model_credential = MiniMaxLLMModelCredential()
minimax_tts_model_credential = MiniMaxTTSModelCredential()

minimax_m2_7 = ModelInfo('MiniMax-M2.7',
                         _('Latest flagship model with enhanced reasoning and coding. 204K context window'),
                         ModelTypeConst.LLM,
                         minimax_llm_model_credential, MiniMaxChatModel)

minimax_m2_7_highspeed = ModelInfo('MiniMax-M2.7-highspeed',
                                   _('High-speed version of M2.7 for low-latency scenarios. 204K context window'),
                                   ModelTypeConst.LLM,
                                   minimax_llm_model_credential, MiniMaxChatModel)

minimax_m2_5 = ModelInfo('MiniMax-M2.5',
                         _('Peak Performance. Ultimate Value. 204K context window'),
                         ModelTypeConst.LLM,
                         minimax_llm_model_credential, MiniMaxChatModel)

minimax_m2_5_highspeed = ModelInfo('MiniMax-M2.5-highspeed',
                                   _('Same performance, faster and more agile. 204K context window'),
                                   ModelTypeConst.LLM,
                                   minimax_llm_model_credential, MiniMaxChatModel)

minimax_tts_hd = ModelInfo('speech-2.8-hd',
                           _('Perfecting tonal nuances with maximized timbre similarity'),
                           ModelTypeConst.TTS,
                           minimax_tts_model_credential, MiniMaxTextToSpeech)

minimax_tts_turbo = ModelInfo('speech-2.8-turbo',
                              _('Faster, more affordable TTS model'),
                              ModelTypeConst.TTS,
                              minimax_tts_model_credential, MiniMaxTextToSpeech)

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info(minimax_m2_7)
    .append_model_info(minimax_m2_7_highspeed)
    .append_model_info(minimax_m2_5)
    .append_model_info(minimax_m2_5_highspeed)
    .append_default_model_info(minimax_m2_7)
    .append_model_info(minimax_tts_hd)
    .append_model_info(minimax_tts_turbo)
    .append_default_model_info(minimax_tts_hd)
    .build()
)


class MiniMaxModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_minimax_provider', name='MiniMax', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", 'models_provider', 'impl', 'minimax_model_provider', 'icon',
                         'minimax_icon_svg')))
