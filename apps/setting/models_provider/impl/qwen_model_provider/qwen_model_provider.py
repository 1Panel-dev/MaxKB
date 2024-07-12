# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： qwen_model_provider.py
    @date：2023/10/31 16:19
    @desc:
"""
import os

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import ModelProvideInfo, ModelTypeConst, ModelInfo, IModelProvider, \
    ModelInfoManage
from setting.models_provider.impl.qwen_model_provider.credential.llm import OpenAILLMModelCredential

from setting.models_provider.impl.qwen_model_provider.model.llm import QwenChatModel
from smartdoc.conf import PROJECT_DIR

qwen_model_credential = OpenAILLMModelCredential()

module_info_list = [
    ModelInfo('qwen-turbo', '', ModelTypeConst.LLM, qwen_model_credential, QwenChatModel),
    ModelInfo('qwen-plus', '', ModelTypeConst.LLM, qwen_model_credential, QwenChatModel),
    ModelInfo('qwen-max', '', ModelTypeConst.LLM, qwen_model_credential, QwenChatModel)
]

model_info_manage = ModelInfoManage.builder().append_model_info_list(module_info_list).append_default_model_info(
    ModelInfo('qwen-turbo', '', ModelTypeConst.LLM, qwen_model_credential, QwenChatModel)).build()


class QwenModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_qwen_provider', name='通义千问', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'qwen_model_provider', 'icon',
                         'qwen_icon_svg')))
