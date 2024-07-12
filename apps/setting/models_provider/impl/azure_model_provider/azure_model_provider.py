# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： azure_model_provider.py
    @date：2023/10/31 16:19
    @desc:
"""
import os

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, \
    ModelTypeConst, ModelInfoManage
from setting.models_provider.impl.azure_model_provider.credential.llm import AzureLLMModelCredential
from setting.models_provider.impl.azure_model_provider.model.azure_chat_model import AzureChatModel
from smartdoc.conf import PROJECT_DIR

base_azure_llm_model_credential = AzureLLMModelCredential()

default_model_info = ModelInfo('Azure OpenAI', '具体的基础模型由部署名决定', ModelTypeConst.LLM,
                               base_azure_llm_model_credential, AzureChatModel, api_version='2024-02-15-preview'
                               )

model_info_manage = ModelInfoManage.builder().append_default_model_info(default_model_info).append_model_info(
    default_model_info).build()


class AzureModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_azure_provider', name='Azure OpenAI', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'azure_model_provider', 'icon',
                         'azure_icon_svg')))
