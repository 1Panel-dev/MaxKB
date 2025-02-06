# coding=utf-8
import os
from urllib.parse import urlparse, ParseResult

import requests

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, ModelTypeConst, \
    ModelInfoManage
from setting.models_provider.impl.vllm_model_provider.credential.embedding import VllmEmbeddingCredential
from setting.models_provider.impl.vllm_model_provider.credential.image import VllmImageModelCredential
from setting.models_provider.impl.vllm_model_provider.credential.llm import VLLMModelCredential
from setting.models_provider.impl.vllm_model_provider.model.embedding import VllmEmbeddingModel
from setting.models_provider.impl.vllm_model_provider.model.image import VllmImage
from setting.models_provider.impl.vllm_model_provider.model.llm import VllmChatModel
from smartdoc.conf import PROJECT_DIR
from django.utils.translation import gettext as _

v_llm_model_credential = VLLMModelCredential()
image_model_credential = VllmImageModelCredential()
embedding_model_credential = VllmEmbeddingCredential()

model_info_list = [
    ModelInfo('facebook/opt-125m', _('Facebook’s 125M parameter model'), ModelTypeConst.LLM, v_llm_model_credential, VllmChatModel),
    ModelInfo('BAAI/Aquila-7B', _('BAAI’s 7B parameter model'), ModelTypeConst.LLM, v_llm_model_credential, VllmChatModel),
    ModelInfo('BAAI/AquilaChat-7B', _('BAAI’s 13B parameter mode'), ModelTypeConst.LLM, v_llm_model_credential, VllmChatModel),

]

image_model_info_list = [
    ModelInfo('Qwen/Qwen2-VL-2B-Instruct', '', ModelTypeConst.IMAGE, image_model_credential, VllmImage),
]

embedding_model_info_list = [
    ModelInfo('HIT-TMG/KaLM-embedding-multilingual-mini-instruct-v1.5', '', ModelTypeConst.EMBEDDING, embedding_model_credential, VllmEmbeddingModel),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_default_model_info(ModelInfo('facebook/opt-125m',
                                         _('Facebook’s 125M parameter model'),
                                         ModelTypeConst.LLM, v_llm_model_credential, VllmChatModel))
    .append_model_info_list(image_model_info_list)
    .append_default_model_info(image_model_info_list[0])
    .append_model_info_list(embedding_model_info_list)
    .append_default_model_info(embedding_model_info_list[0])
    .build()
)


def get_base_url(url: str):
    parse = urlparse(url)
    result_url = ParseResult(scheme=parse.scheme, netloc=parse.netloc, path=parse.path, params='',
                             query='',
                             fragment='').geturl()
    return result_url[:-1] if result_url.endswith("/") else result_url


class VllmModelProvider(IModelProvider):
    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_vllm_provider', name='vLLM', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'vllm_model_provider', 'icon',
                         'vllm_icon_svg')))

    @staticmethod
    def get_base_model_list(api_base, api_key):
        base_url = get_base_url(api_base)
        base_url = base_url if base_url.endswith('/v1') else (base_url + '/v1')
        headers = {}
        if api_key:
            headers['Authorization'] = f"Bearer {api_key}"
        r = requests.request(method="GET", url=f"{base_url}/models", headers=headers, timeout=5)
        r.raise_for_status()
        return r.json().get('data')

    @staticmethod
    def get_model_info_by_name(model_list, model_name):
        if model_list is None:
            return []
        return [model for model in model_list if model.get('id') == model_name]
