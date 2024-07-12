# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： zhipu_model_provider.py
    @date：2024/04/19 13:5
    @desc:
"""
import os

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import ModelProvideInfo, ModelTypeConst, ModelInfo, IModelProvider, \
    ModelInfoManage
from setting.models_provider.impl.zhipu_model_provider.credential.llm import ZhiPuLLMModelCredential
from setting.models_provider.impl.zhipu_model_provider.model.llm import ZhipuChatModel
from smartdoc.conf import PROJECT_DIR

qwen_model_credential = ZhiPuLLMModelCredential()
model_info_list = [
    ModelInfo('glm-4', '', ModelTypeConst.LLM, qwen_model_credential, ZhipuChatModel),
    ModelInfo('glm-4v', '', ModelTypeConst.LLM, qwen_model_credential, ZhipuChatModel),
    ModelInfo('glm-3-turbo', '', ModelTypeConst.LLM, qwen_model_credential, ZhipuChatModel)
]
model_info_manage = ModelInfoManage.builder().append_model_info_list(model_info_list).append_model_info(
    ModelInfo('glm-4', '', ModelTypeConst.LLM, qwen_model_credential, ZhipuChatModel)).build()


class ZhiPuModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_zhipu_provider', name='智谱AI', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'zhipu_model_provider', 'icon',
                         'zhipuai_icon_svg')))
