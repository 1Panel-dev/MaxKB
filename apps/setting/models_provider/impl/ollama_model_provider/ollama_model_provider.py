# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： ollama_model_provider.py
    @date：2024/3/5 17:23
    @desc:
"""
import os
from typing import Dict

from langchain.chat_models.base import BaseChatModel
from langchain.schema import HumanMessage

from common import froms
from common.exception.app_exception import AppApiException
from common.froms import BaseForm
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, ModelTypeConst, \
    BaseModelCredential
from setting.models_provider.impl.ollama_model_provider.model.ollama_chat_model import OllamaChatModel
from smartdoc.conf import PROJECT_DIR


class OllamaLLMModelCredential(BaseForm, BaseModelCredential):
    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], raise_exception=False):
        model_type_list = OllamaModelProvider().get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(500, f'{model_type} 模型类型不支持')

        if model_name not in model_dict:
            raise AppApiException(500, f'{model_name} 模型名称不支持')

        for key in ['api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(500, f'{key} 字段为必填字段')
                else:
                    return False
        try:
            OllamaModelProvider().get_model(model_type, model_name, model_credential).invoke(
                [HumanMessage(content='valid')])
        except Exception as e:
            if raise_exception:
                raise AppApiException(500, "校验失败,请检查 api_key secret_key 是否正确")
        return True

    def encryption_dict(self, model_info: Dict[str, object]):
        return {**model_info, 'api_key': super().encryption(model_info.get('api_key', ''))}

    def build_model(self, model_info: Dict[str, object]):
        for key in ['api_key', 'model']:
            if key not in model_info:
                raise AppApiException(500, f'{key} 字段为必填字段')
        self.api_key = model_info.get('api_key')
        return self

    api_base = froms.TextInputField('API 域名', required=True)
    api_key = froms.PasswordInputField('API Key', required=True)


ollama_llm_model_credential = OllamaLLMModelCredential()

model_dict = {
    'llama2': ModelInfo(
        'llama2',
        'Llama 2 是一组经过预训练和微调的生成文本模型，其规模从 70 亿到 700 亿个不等。这是 7B 预训练模型的存储库。其他模型的链接可以在底部的索引中找到。',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'llama2:13b': ModelInfo(
        'llama2:13b',
        'Llama 2 是一组经过预训练和微调的生成文本模型，其规模从 70 亿到 700 亿个不等。这是 13B 预训练模型的存储库。其他模型的链接可以在底部的索引中找到。',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'llama2:70b': ModelInfo(
        'llama2:70b',
        'Llama 2 是一组经过预训练和微调的生成文本模型，其规模从 70 亿到 700 亿个不等。这是 70B 预训练模型的存储库。其他模型的链接可以在底部的索引中找到。',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'llama2-chinese:13b': ModelInfo(
        'llama2-chinese:13b',
        '由于Llama2本身的中文对齐较弱，我们采用中文指令集，对meta-llama/Llama-2-13b-chat-hf进行LoRA微调，使其具备较强的中文对话能力。',
        ModelTypeConst.LLM, ollama_llm_model_credential),
    'llama2-chinese:13b-maxkb': ModelInfo(
        'llama2-chinese:13b-maxkb',
        '由于Llama2本身的中文对齐较弱，我们采用中文指令集，对meta-llama/Llama-2-13b-chat-hf进行LoRA微调，使其具备较强的中文对话能力。fi2cloud专用',
        ModelTypeConst.LLM, ollama_llm_model_credential),
}


class OllamaModelProvider(IModelProvider):
    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_ollama_provider', name='Ollama', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'ollama_model_provider', 'icon',
                         'ollama_icon_svg')))

    def get_model_type_list(self):
        return [{'key': "大语言模型", 'value': "LLM"}]

    def get_model_list(self, model_type):
        if model_type is None:
            raise AppApiException(500, '模型类型不能为空')
        return [model_dict.get(key).to_dict() for key in
                list(filter(lambda key: model_dict.get(key).model_type == model_type, model_dict.keys()))]

    def get_model_credential(self, model_type, model_name):
        if model_name in model_dict:
            return model_dict.get(model_name).model_credential
        raise AppApiException(500, f'不支持的模型:{model_name}')

    def get_model(self, model_type, model_name, model_credential: Dict[str, object], **model_kwargs) -> BaseChatModel:
        return OllamaChatModel(model=model_name, openai_api_base=model_credential.get('api_base'),
                               openai_api_key=model_credential.get('api_key'))

    def get_dialogue_number(self):
        return 2
