# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： azure_model_provider.py
    @date：2023/10/31 16:19
    @desc:
"""
import os
from typing import Dict

from langchain.schema import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, BaseModelCredential, \
    ModelInfo, \
    ModelTypeConst, ValidCode
from setting.models_provider.impl.azure_model_provider.model.azure_chat_model import AzureChatModel
from smartdoc.conf import PROJECT_DIR


class DefaultAzureLLMModelCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], raise_exception=False):
        model_type_list = AzureModelProvider().get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')

        for key in ['api_base', 'api_key', 'deployment_name', 'api_version']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            model = AzureModelProvider().get_model(model_type, model_name, model_credential)
            model.invoke([HumanMessage(content='你好')])
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, '校验失败,请检查参数是否正确')
            else:
                return False

        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'api_key': super().encryption(model.get('api_key', ''))}

    api_version = forms.TextInputField("API 版本 (api_version)", required=True)

    api_base = forms.TextInputField('API 域名 (azure_endpoint)', required=True)

    api_key = forms.PasswordInputField("API Key (api_key)", required=True)

    deployment_name = forms.TextInputField("部署名 (deployment_name)", required=True)


base_azure_llm_model_credential = DefaultAzureLLMModelCredential()

model_dict = {
    'deployment_name': ModelInfo('Azure OpenAI', '具体的基础模型由部署名决定', ModelTypeConst.LLM,
                                 base_azure_llm_model_credential, api_version='2024-02-15-preview'
                                 )
}


class AzureModelProvider(IModelProvider):

    def get_dialogue_number(self):
        return 3

    def get_model(self, model_type, model_name, model_credential: Dict[str, object], **model_kwargs) -> AzureChatModel:
        azure_chat_open_ai = AzureChatModel(
            azure_endpoint=model_credential.get('api_base'),
            openai_api_version=model_credential.get('api_version', '2024-02-15-preview'),
            deployment_name=model_credential.get('deployment_name'),
            openai_api_key=model_credential.get('api_key'),
            openai_api_type="azure"
        )
        return azure_chat_open_ai

    def get_model_credential(self, model_type, model_name):
        if model_name in model_dict:
            return model_dict.get(model_name).model_credential
        return base_azure_llm_model_credential

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_azure_provider', name='Azure OpenAI', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'azure_model_provider', 'icon',
                         'azure_icon_svg')))

    def get_model_list(self, model_type: str):
        if model_type is None:
            raise AppApiException(500, '模型类型不能为空')
        return [model_dict.get(key).to_dict() for key in
                list(filter(lambda key: model_dict.get(key).model_type == model_type, model_dict.keys()))]

    def get_model_type_list(self):
        return [{'key': "大语言模型", 'value': "LLM"}]
