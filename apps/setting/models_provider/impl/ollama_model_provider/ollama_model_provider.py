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

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, ModelTypeConst, \
    BaseModelCredential, DownModelChunk, DownModelChunkStatus, ValidCode, ModelInfoManage
from setting.models_provider.impl.ollama_model_provider.credential.embedding import OllamaEmbeddingModelCredential
from setting.models_provider.impl.ollama_model_provider.credential.llm import OllamaLLMModelCredential
from setting.models_provider.impl.ollama_model_provider.model.embedding import OllamaEmbedding
from setting.models_provider.impl.ollama_model_provider.model.llm import OllamaChatModel
from smartdoc.conf import PROJECT_DIR

""

ollama_llm_model_credential = OllamaLLMModelCredential()
model_info_list = [
    ModelInfo(
        'llama2',
        'Llama 2 是一组经过预训练和微调的生成文本模型，其规模从 70 亿到 700 亿个不等。这是 7B 预训练模型的存储库。其他模型的链接可以在底部的索引中找到。',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'llama2:13b',
        'Llama 2 是一组经过预训练和微调的生成文本模型，其规模从 70 亿到 700 亿个不等。这是 13B 预训练模型的存储库。其他模型的链接可以在底部的索引中找到。',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'llama2:70b',
        'Llama 2 是一组经过预训练和微调的生成文本模型，其规模从 70 亿到 700 亿个不等。这是 70B 预训练模型的存储库。其他模型的链接可以在底部的索引中找到。',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'llama2-chinese:13b',
        '由于Llama2本身的中文对齐较弱，我们采用中文指令集，对meta-llama/Llama-2-13b-chat-hf进行LoRA微调，使其具备较强的中文对话能力。',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'llama3:8b',
        'Meta Llama 3：迄今为止最有能力的公开产品LLM。80亿参数。',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'llama3:70b',
        'Meta Llama 3：迄今为止最有能力的公开产品LLM。700亿参数。',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen:0.5b',
        'qwen 1.5 0.5b 相较于以往版本，模型与人类偏好的对齐程度以及多语言处理能力上有显著增强。所有规模的模型都支持32768个tokens的上下文长度。5亿参数。',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen:1.8b',
        'qwen 1.5 1.8b 相较于以往版本，模型与人类偏好的对齐程度以及多语言处理能力上有显著增强。所有规模的模型都支持32768个tokens的上下文长度。18亿参数。',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen:4b',
        'qwen 1.5 4b 相较于以往版本，模型与人类偏好的对齐程度以及多语言处理能力上有显著增强。所有规模的模型都支持32768个tokens的上下文长度。40亿参数。',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),

    ModelInfo(
        'qwen:7b',
        'qwen 1.5 7b 相较于以往版本，模型与人类偏好的对齐程度以及多语1言处理能力上有显著增强。所有规模的模型都支持32768个tokens的上下文长度。70亿参数。',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen:14b',
        'qwen 1.5 14b 相较于以往版本，模型与人类偏好的对齐程度以及多语言处理能力上有显著增强。所有规模的模型都支持32768个tokens的上下文长度。140亿参数。',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen:32b',
        'qwen 1.5 32b 相较于以往版本，模型与人类偏好的对齐程度以及多语言处理能力上有显著增强。所有规模的模型都支持32768个tokens的上下文长度。320亿参数。',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen:72b',
        'qwen 1.5 72b 相较于以往版本，模型与人类偏好的对齐程度以及多语言处理能力上有显著增强。所有规模的模型都支持32768个tokens的上下文长度。720亿参数。',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen:110b',
        'qwen 1.5 110b 相较于以往版本，模型与人类偏好的对齐程度以及多语言处理能力上有显著增强。所有规模的模型都支持32768个tokens的上下文长度。1100亿参数。',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'phi3',
        'Phi-3 Mini是Microsoft的3.8B参数，轻量级，最先进的开放模型。',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
]
ollama_embedding_model_credential = OllamaEmbeddingModelCredential()
embedding_model_info = [
    ModelInfo(
        'nomic-embed-text',
        '一个具有大令牌上下文窗口的高性能开放嵌入模型。',
        ModelTypeConst.EMBEDDING, ollama_embedding_model_credential, OllamaEmbedding),
]

model_info_manage = ModelInfoManage.builder().append_model_info_list(model_info_list).append_model_info_list(
    embedding_model_info).append_default_model_info(
    ModelInfo(
        'phi3',
        'Phi-3 Mini是Microsoft的3.8B参数，轻量级，最先进的开放模型。',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel)).append_default_model_info(ModelInfo(
    'nomic-embed-text',
    '一个具有大令牌上下文窗口的高性能开放嵌入模型。',
    ModelTypeConst.EMBEDDING, ollama_embedding_model_credential, OllamaEmbedding), ).build()


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
        rows = [t for t in temp.split("\n") if len(t) > 0]
        for row in rows:
            yield convert_to_down_model_chunk(row, index)


class OllamaModelProvider(IModelProvider):
    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_ollama_provider', name='Ollama', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'ollama_model_provider', 'icon',
                         'ollama_icon_svg')))

    @staticmethod
    def get_base_model_list(api_base):
        base_url = get_base_url(api_base)
        r = requests.request(method="GET", url=f"{base_url}/api/tags", timeout=5)
        r.raise_for_status()
        return r.json()

    def down_model(self, model_type: str, model_name, model_credential: Dict[str, object]) -> Iterator[DownModelChunk]:
        api_base = model_credential.get('api_base', '')
        base_url = get_base_url(api_base)
        r = requests.request(
            method="POST",
            url=f"{base_url}/api/pull",
            data=json.dumps({"name": model_name}).encode(),
            stream=True,
        )
        return convert(r)
