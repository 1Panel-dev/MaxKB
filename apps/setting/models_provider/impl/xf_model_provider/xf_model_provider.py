# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： xf_model_provider.py
    @date：2024/04/19 14:47
    @desc:
"""
import os
from typing import Dict

from langchain.schema import HumanMessage
from langchain_community.chat_models import ChatSparkLLM

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import ModelProvideInfo, ModelTypeConst, BaseModelCredential, \
    ModelInfo, IModelProvider, ValidCode
from setting.models_provider.impl.xf_model_provider.model.xf_chat_model import XFChatSparkLLM
from smartdoc.conf import PROJECT_DIR
import ssl

ssl._create_default_https_context = ssl.create_default_context()


class XunFeiLLMModelCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], raise_exception=False):
        model_type_list = XunFeiModelProvider().get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')

        for key in ['spark_api_url', 'spark_app_id', 'spark_api_key', 'spark_api_secret']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            model = XunFeiModelProvider().get_model(model_type, model_name, model_credential)
            model.invoke([HumanMessage(content='你好')])
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'校验失败,请检查参数是否正确: {str(e)}')
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'spark_api_secret': super().encryption(model.get('spark_api_secret', ''))}

    spark_api_url = forms.TextInputField('API 域名', required=True)
    spark_app_id = forms.TextInputField('APP ID', required=True)
    spark_api_key = forms.PasswordInputField("API Key", required=True)
    spark_api_secret = forms.PasswordInputField('API Secret', required=True)


qwen_model_credential = XunFeiLLMModelCredential()

model_dict = {
    'generalv3.5': ModelInfo('generalv3.5', '', ModelTypeConst.LLM, qwen_model_credential),
    'generalv3': ModelInfo('generalv3', '', ModelTypeConst.LLM, qwen_model_credential),
    'generalv2': ModelInfo('generalv2', '', ModelTypeConst.LLM, qwen_model_credential)
}


class XunFeiModelProvider(IModelProvider):

    def get_dialogue_number(self):
        return 3

    def get_model(self, model_type, model_name, model_credential: Dict[str, object], **model_kwargs) -> XFChatSparkLLM:
        zhipuai_chat = XFChatSparkLLM(
            spark_app_id=model_credential.get('spark_app_id'),
            spark_api_key=model_credential.get('spark_api_key'),
            spark_api_secret=model_credential.get('spark_api_secret'),
            spark_api_url=model_credential.get('spark_api_url'),
            spark_llm_domain=model_name
        )
        return zhipuai_chat

    def get_model_credential(self, model_type, model_name):
        if model_name in model_dict:
            return model_dict.get(model_name).model_credential
        return qwen_model_credential

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_xf_provider', name='讯飞星火', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'xf_model_provider', 'icon',
                         'xf_icon_svg')))

    def get_model_list(self, model_type: str):
        if model_type is None:
            raise AppApiException(500, '模型类型不能为空')
        return [model_dict.get(key).to_dict() for key in
                list(filter(lambda key: model_dict.get(key).model_type == model_type, model_dict.keys()))]

    def get_model_type_list(self):
        return [{'key': "大语言模型", 'value': "LLM"}]
