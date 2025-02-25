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
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, ModelTypeConst, \
    BaseModelCredential, DownModelChunk, DownModelChunkStatus, ValidCode, ModelInfoManage
from setting.models_provider.impl.ollama_model_provider.credential.embedding import OllamaEmbeddingModelCredential
from setting.models_provider.impl.ollama_model_provider.credential.image import OllamaImageModelCredential
from setting.models_provider.impl.ollama_model_provider.credential.llm import OllamaLLMModelCredential
from setting.models_provider.impl.ollama_model_provider.credential.reranker import OllamaReRankModelCredential
from setting.models_provider.impl.ollama_model_provider.model.embedding import OllamaEmbedding
from setting.models_provider.impl.ollama_model_provider.model.image import OllamaImage
from setting.models_provider.impl.ollama_model_provider.model.llm import OllamaChatModel
from setting.models_provider.impl.ollama_model_provider.model.reranker import OllamaReranker
from smartdoc.conf import PROJECT_DIR
from django.utils.translation import gettext as _

""

ollama_llm_model_credential = OllamaLLMModelCredential()
model_info_list = [
    ModelInfo(
        'deepseek-r1:1.5b',
        '',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'deepseek-r1:7b',
        '',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'deepseek-r1:8b',
        '',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'deepseek-r1:14b',
        '',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'deepseek-r1:32b',
        '',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),

    ModelInfo(
        'llama2',
        _('Llama 2 is a set of pretrained and fine-tuned generative text models ranging in size from 7 billion to 70 billion. This is a repository of 7B pretrained models. Links to other models can be found in the index at the bottom.'),
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'llama2:13b',
        _('Llama 2 is a set of pretrained and fine-tuned generative text models ranging in size from 7 billion to 70 billion. This is a repository of 13B pretrained models. Links to other models can be found in the index at the bottom.'),
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'llama2:70b',
        _('Llama 2 is a set of pretrained and fine-tuned generative text models ranging in size from 7 billion to 70 billion. This is a repository of 70B pretrained models. Links to other models can be found in the index at the bottom.'),
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'llama2-chinese:13b',
        _('Since the Chinese alignment of Llama2 itself is weak, we use the Chinese instruction set to fine-tune meta-llama/Llama-2-13b-chat-hf with LoRA so that it has strong Chinese conversation capabilities.'),
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'llama3:8b',
        _('Meta Llama 3: The most capable public product LLM to date. 8 billion parameters.'),
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'llama3:70b',
        _('Meta Llama 3: The most capable public product LLM to date. 70 billion parameters.'),
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen:0.5b',
        _("Compared with previous versions, qwen 1.5 0.5b has significantly enhanced the model's alignment with human preferences and its multi-language processing capabilities. Models of all sizes support a context length of 32768 tokens. 500 million parameters."),
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen:1.8b',
        _("Compared with previous versions, qwen 1.5 1.8b has significantly enhanced the model's alignment with human preferences and its multi-language processing capabilities. Models of all sizes support a context length of 32768 tokens. 1.8 billion parameters."),
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen:4b',
        _("Compared with previous versions, qwen 1.5 4b has significantly enhanced the model's alignment with human preferences and its multi-language processing capabilities. Models of all sizes support a context length of 32768 tokens. 4 billion parameters."),
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),

    ModelInfo(
        'qwen:7b',
        _("Compared with previous versions, qwen 1.5 7b has significantly enhanced the model's alignment with human preferences and its multi-language processing capabilities. Models of all sizes support a context length of 32768 tokens. 7 billion parameters."),
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen:14b',
        _("Compared with previous versions, qwen 1.5 14b has significantly enhanced the model's alignment with human preferences and its multi-language processing capabilities. Models of all sizes support a context length of 32768 tokens. 14 billion parameters."),
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen:32b',
        _("Compared with previous versions, qwen 1.5 32b has significantly enhanced the model's alignment with human preferences and its multi-language processing capabilities. Models of all sizes support a context length of 32768 tokens. 32 billion parameters."),
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen:72b',
        _("Compared with previous versions, qwen 1.5 72b has significantly enhanced the model's alignment with human preferences and its multi-language processing capabilities. Models of all sizes support a context length of 32768 tokens. 72 billion parameters."),
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen:110b',
        _("Compared with previous versions, qwen 1.5 110b has significantly enhanced the model's alignment with human preferences and its multi-language processing capabilities. Models of all sizes support a context length of 32768 tokens. 110 billion parameters."),
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen2:72b-instruct',
        '',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen2:57b-a14b-instruct',
        '',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen2:7b-instruct',
        '',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen2.5:72b-instruct',
        '',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen2.5:32b-instruct',
        '',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen2.5:14b-instruct',
        '',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen2.5:7b-instruct',
        '',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen2.5:1.5b-instruct',
        '',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen2.5:0.5b-instruct',
        '',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'qwen2.5:3b-instruct',
        '',
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
    ModelInfo(
        'phi3',
        _("Phi-3 Mini is Microsoft's 3.8B parameter, lightweight, state-of-the-art open model."),
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel),
]
ollama_embedding_model_credential = OllamaEmbeddingModelCredential()
ollama_image_model_credential = OllamaImageModelCredential()
ollama_reranker_model_credential = OllamaReRankModelCredential()
embedding_model_info = [
    ModelInfo(
        'nomic-embed-text',
        _('A high-performance open embedding model with a large token context window.'),
        ModelTypeConst.EMBEDDING, ollama_embedding_model_credential, OllamaEmbedding),
]
reranker_model_info = [
    ModelInfo(
        'linux6200/bge-reranker-v2-m3',
        '',
        ModelTypeConst.RERANKER, ollama_reranker_model_credential, OllamaReranker),
]

image_model_info = [
    ModelInfo(
        'llava:7b',
        '',
        ModelTypeConst.IMAGE, ollama_image_model_credential, OllamaImage),
    ModelInfo(
        'llava:13b',
        '',
        ModelTypeConst.IMAGE, ollama_image_model_credential, OllamaImage),
    ModelInfo(
        'llava:34b',
        '',
        ModelTypeConst.IMAGE, ollama_image_model_credential, OllamaImage),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_model_info_list(embedding_model_info)
    .append_default_model_info(ModelInfo(
        'phi3',
        _('Phi-3 Mini is Microsoft\'s 3.8B parameter, lightweight, state-of-the-art open model.'),
        ModelTypeConst.LLM, ollama_llm_model_credential, OllamaChatModel))
    .append_default_model_info(ModelInfo(
        'nomic-embed-text',
        _('A high-performance open embedding model with a large token context window.'),
        ModelTypeConst.EMBEDDING, ollama_embedding_model_credential, OllamaEmbedding), )
    .append_model_info_list(image_model_info)
    .append_default_model_info(image_model_info[0])
    .append_model_info_list(reranker_model_info)
    .append_default_model_info(reranker_model_info[0])
    .build()
)


def get_base_url(url: str):
    parse = urlparse(url)
    result_url = ParseResult(scheme=parse.scheme, netloc=parse.netloc, path=parse.path, params='',
                             query='',
                             fragment='').geturl()
    return result_url[:-1] if result_url.endswith("/") else result_url


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
