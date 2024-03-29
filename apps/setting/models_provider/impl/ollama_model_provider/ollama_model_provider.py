# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： ollama_model_provider.py
    @date：2024/3/5 17:23
    @desc:
"""
import json
import os
from typing import Dict, Iterator
from urllib.parse import urlparse, ParseResult

import requests
from langchain.chat_models.base import BaseChatModel

from common import froms
from common.exception.app_exception import AppApiException
from common.froms import BaseForm
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, ModelTypeConst, \
    BaseModelCredential, DownModelChunk, DownModelChunkStatus, ValidCode
from setting.models_provider.impl.ollama_model_provider.model.ollama_chat_model import OllamaChatModel
from smartdoc.conf import PROJECT_DIR

""


class OllamaLLMModelCredential(BaseForm, BaseModelCredential):
    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], raise_exception=False):
        model_type_list = OllamaModelProvider().get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')
        try:
            model_list = OllamaModelProvider.get_base_model_list(model_credential.get('api_base'))
        except Exception as e:
            raise AppApiException(ValidCode.valid_error.value, "API 域名无效")
        exist = [model for model in model_list.get('models') if
                 model.get('model') == model_name or model.get('model').replace(":latest", "") == model_name]
        if len(exist) == 0:
            raise AppApiException(ValidCode.model_not_fount, "模型不存在,请先下载模型")
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
        ModelTypeConst.LLM, ollama_llm_model_credential)
}


def get_base_url(url: str):
    parse = urlparse(url)
    return ParseResult(scheme=parse.scheme, netloc=parse.netloc, path='', params='',
                       query='',
                       fragment='').geturl()


def convert_to_down_model_chunk(row_str: str, chunk_index: int):
    row = json.loads(row_str)
    status = DownModelChunkStatus.unknown
    digest = ""
    progress = 100
    if 'status' in row:
        digest = row.get('status')
        if row.get('status') == 'success':
            status = DownModelChunkStatus.success
        if row.get('status').__contains__("pulling"):
            progress = 0
            status = DownModelChunkStatus.pulling
            if 'total' in row and 'completed' in row:
                progress = (row.get('completed') / row.get('total') * 100)
    elif 'error' in row:
        status = DownModelChunkStatus.error
        digest = row.get('error')
    return DownModelChunk(status=status, digest=digest, progress=progress, details=row_str, index=chunk_index)


def convert(response_stream) -> Iterator[DownModelChunk]:
    temp = ""
    index = 0
    for c in response_stream:
        index += 1
        row_content = c.decode()
        temp += row_content
        if row_content.endswith('}') or row_content.endswith('\n'):
            rows = [t for t in temp.split("\n") if len(t) > 0]
            for row in rows:
                yield convert_to_down_model_chunk(row, index)
            temp = ""

    if len(temp) > 0:
        print(temp)
        rows = [t for t in temp.split("\n") if len(t) > 0]
        for row in rows:
            yield convert_to_down_model_chunk(row, index)


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
        # 如果使用模型不在配置中,则使用默认认证
        return ollama_llm_model_credential

    def get_model(self, model_type, model_name, model_credential: Dict[str, object], **model_kwargs) -> BaseChatModel:
        api_base = model_credential.get('api_base')
        base_url = get_base_url(api_base)
        return OllamaChatModel(model=model_name, openai_api_base=(base_url + '/v1'),
                               openai_api_key=model_credential.get('api_key'))

    def get_dialogue_number(self):
        return 2

    @staticmethod
    def get_base_model_list(api_base):
        base_url = get_base_url(api_base)
        r = requests.request(method="GET", url=f"{base_url}/api/tags", timeout=5)
        r.raise_for_status()
        return r.json()

    def down_model(self, model_type: str, model_name, model_credential: Dict[str, object]) -> Iterator[DownModelChunk]:
        api_base = model_credential.get('api_base')
        base_url = get_base_url(api_base)
        r = requests.request(
            method="POST",
            url=f"{base_url}/api/pull",
            data=json.dumps({"name": model_name}).encode(),
            stream=True,
        )
        return convert(r)
