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
from setting.models_provider.impl.xf_model_provider.credential.llm import XunFeiLLMModelCredential
from setting.models_provider.impl.xf_model_provider.credential.stt import XunFeiSTTModelCredential
from setting.models_provider.impl.xf_model_provider.credential.tts import XunFeiTTSModelCredential
from setting.models_provider.impl.xf_model_provider.model.llm import XFChatSparkLLM
from setting.models_provider.impl.xf_model_provider.model.stt import XFSparkSpeechToText
from setting.models_provider.impl.xf_model_provider.model.tts import XFSparkTextToSpeech
from smartdoc.conf import PROJECT_DIR

ssl._create_default_https_context = ssl.create_default_context()

qwen_model_credential = XunFeiLLMModelCredential()
stt_model_credential = XunFeiSTTModelCredential()
tts_model_credential = XunFeiTTSModelCredential()
model_info_list = [
    ModelInfo('generalv3.5', '', ModelTypeConst.LLM, qwen_model_credential, XFChatSparkLLM),
    ModelInfo('generalv3', '', ModelTypeConst.LLM, qwen_model_credential, XFChatSparkLLM),
    ModelInfo('generalv2', '', ModelTypeConst.LLM, qwen_model_credential, XFChatSparkLLM),
    ModelInfo('iat', '中英文识别', ModelTypeConst.STT, stt_model_credential, XFSparkSpeechToText),
    ModelInfo('tts', '', ModelTypeConst.TTS, tts_model_credential, XFSparkTextToSpeech),
]

model_info_manage = ModelInfoManage.builder().append_model_info_list(model_info_list).append_default_model_info(
    ModelInfo('generalv3.5', '', ModelTypeConst.LLM, qwen_model_credential, XFChatSparkLLM)).build()


class XunFeiModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_xf_provider', name='讯飞星火', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'xf_model_provider', 'icon',
                         'xf_icon_svg')))
