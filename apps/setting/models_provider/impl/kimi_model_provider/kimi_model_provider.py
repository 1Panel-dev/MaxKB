# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： kimi_model_provider.py
    @date：2024/3/28 16:26
    @desc:
"""
import os

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, \
    ModelTypeConst, ModelInfoManage
from setting.models_provider.impl.kimi_model_provider.credential.llm import KimiLLMModelCredential
from setting.models_provider.impl.kimi_model_provider.model.llm import KimiChatModel
from smartdoc.conf import PROJECT_DIR

kimi_llm_model_credential = KimiLLMModelCredential()

moonshot_v1_8k = ModelInfo('moonshot-v1-8k', '', ModelTypeConst.LLM, kimi_llm_model_credential,
                           KimiChatModel)
moonshot_v1_32k = ModelInfo('moonshot-v1-32k', '', ModelTypeConst.LLM, kimi_llm_model_credential,
                            KimiChatModel)
moonshot_v1_128k = ModelInfo('moonshot-v1-128k', '', ModelTypeConst.LLM, kimi_llm_model_credential,
                             KimiChatModel)

model_info_manage = ModelInfoManage.builder().append_model_info(moonshot_v1_8k).append_model_info(
    moonshot_v1_32k).append_default_model_info(moonshot_v1_128k).append_default_model_info(moonshot_v1_8k).build()


class KimiModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_dialogue_number(self):
        return 3

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_kimi_provider', name='Kimi', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'kimi_model_provider', 'icon',
                         'kimi_icon_svg')))
