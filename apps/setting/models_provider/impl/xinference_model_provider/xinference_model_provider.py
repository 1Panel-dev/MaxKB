# coding=utf-8
import os
from urllib.parse import urlparse, ParseResult

import requests

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, ModelTypeConst, \
    ModelInfoManage
from setting.models_provider.impl.xinference_model_provider.credential.embedding import \
    XinferenceEmbeddingModelCredential
from setting.models_provider.impl.xinference_model_provider.credential.image import XinferenceImageModelCredential
from setting.models_provider.impl.xinference_model_provider.credential.llm import XinferenceLLMModelCredential
from setting.models_provider.impl.xinference_model_provider.credential.reranker import XInferenceRerankerModelCredential
from setting.models_provider.impl.xinference_model_provider.credential.stt import XInferenceSTTModelCredential
from setting.models_provider.impl.xinference_model_provider.credential.tti import XinferenceTextToImageModelCredential
from setting.models_provider.impl.xinference_model_provider.credential.tts import XInferenceTTSModelCredential
from setting.models_provider.impl.xinference_model_provider.model.embedding import XinferenceEmbedding
from setting.models_provider.impl.xinference_model_provider.model.image import XinferenceImage
from setting.models_provider.impl.xinference_model_provider.model.llm import XinferenceChatModel
from setting.models_provider.impl.xinference_model_provider.model.reranker import XInferenceReranker
from setting.models_provider.impl.xinference_model_provider.model.stt import XInferenceSpeechToText
from setting.models_provider.impl.xinference_model_provider.model.tti import XinferenceTextToImage
from setting.models_provider.impl.xinference_model_provider.model.tts import XInferenceTextToSpeech
from smartdoc.conf import PROJECT_DIR
from django.utils.translation import gettext as _

xinference_llm_model_credential = XinferenceLLMModelCredential()
xinference_stt_model_credential = XInferenceSTTModelCredential()
xinference_tts_model_credential = XInferenceTTSModelCredential()
xinference_image_model_credential = XinferenceImageModelCredential()
xinference_tti_model_credential = XinferenceTextToImageModelCredential()

model_info_list = [
    ModelInfo(
        'code-llama',
        _('Code Llama is a language model specifically designed for code generation.'),
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'code-llama-instruct',
        _('''       
Code Llama Instruct is a fine-tuned version of Code Llama's instructions, designed to perform specific tasks.
        '''),
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'code-llama-python',
        _('Code Llama Python is a language model specifically designed for Python code generation.'),
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'codeqwen1.5',
        _('CodeQwen 1.5 is a language model for code generation with high performance.'),
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'codeqwen1.5-chat',
        _('CodeQwen 1.5 Chat is a chat model version of CodeQwen 1.5.'),
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'deepseek',
        _('Deepseek is a large-scale language model with 13 billion parameters.'),
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'deepseek-chat',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'deepseek-coder',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'deepseek-coder-instruct',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'deepseek-vl-chat',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'gpt-3.5-turbo',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'gpt-4',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'gpt-4-vision-preview',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'gpt4all',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'llama2',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'llama2-chat',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'llama2-chat-32k',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen-chat',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen-chat-32k',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen-code',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen-code-chat',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen-vl',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen-vl-chat',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen2-instruct',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen2-72b-instruct',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen2-57b-a14b-instruct',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen2-7b-instruct',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen2.5-72b-instruct',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen2.5-32b-instruct',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen2.5-14b-instruct',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen2.5-7b-instruct',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen2.5-1.5b-instruct',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen2.5-0.5b-instruct',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen2.5-3b-instruct',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'minicpm-llama3-v-2_5',
        '',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
]

voice_model_info = [
    ModelInfo(
        'CosyVoice-300M-SFT',
        '',
        ModelTypeConst.TTS,
        xinference_tts_model_credential,
        XInferenceTextToSpeech
    ),
    ModelInfo(
        'Belle-whisper-large-v3-zh',
        '',
        ModelTypeConst.STT,
        xinference_stt_model_credential,
        XInferenceSpeechToText
    ),
]

image_model_info = [
    ModelInfo(
        'qwen-vl-chat',
        '',
        ModelTypeConst.IMAGE,
        xinference_image_model_credential,
        XinferenceImage
    ),
    ModelInfo(
        'deepseek-vl-chat',
        '',
        ModelTypeConst.IMAGE,
        xinference_image_model_credential,
        XinferenceImage
    ),
    ModelInfo(
        'yi-vl-chat',
        '',
        ModelTypeConst.IMAGE,
        xinference_image_model_credential,
        XinferenceImage
    ),
    ModelInfo(
        'omnilmm',
        '',
        ModelTypeConst.IMAGE,
        xinference_image_model_credential,
        XinferenceImage
    ),
    ModelInfo(
        'internvl-chat',
        '',
        ModelTypeConst.IMAGE,
        xinference_image_model_credential,
        XinferenceImage
    ),
    ModelInfo(
        'cogvlm2',
        '',
        ModelTypeConst.IMAGE,
        xinference_image_model_credential,
        XinferenceImage
    ),
    ModelInfo(
        'MiniCPM-Llama3-V-2_5',
        '',
        ModelTypeConst.IMAGE,
        xinference_image_model_credential,
        XinferenceImage
    ),
    ModelInfo(
        'GLM-4V',
        '',
        ModelTypeConst.IMAGE,
        xinference_image_model_credential,
        XinferenceImage
    ),
    ModelInfo(
        'MiniCPM-V-2.6',
        '',
        ModelTypeConst.IMAGE,
        xinference_image_model_credential,
        XinferenceImage
    ),
    ModelInfo(
        'internvl2',
        '',
        ModelTypeConst.IMAGE,
        xinference_image_model_credential,
        XinferenceImage
    ),
    ModelInfo(
        'qwen2-vl-instruct',
        '',
        ModelTypeConst.IMAGE,
        xinference_image_model_credential,
        XinferenceImage
    ),
    ModelInfo(
        'llama-3.2-vision',
        '',
        ModelTypeConst.IMAGE,
        xinference_image_model_credential,
        XinferenceImage
    ),
    ModelInfo(
        'llama-3.2-vision-instruct',
        '',
        ModelTypeConst.IMAGE,
        xinference_image_model_credential,
        XinferenceImage
    ),
    ModelInfo(
        'glm-edge-v',
        '',
        ModelTypeConst.IMAGE,
        xinference_image_model_credential,
        XinferenceImage
    ),
]

tti_model_info = [
    ModelInfo(
        'sd-turbo',
        '',
        ModelTypeConst.TTI,
        xinference_tti_model_credential,
        XinferenceTextToImage
    ),
    ModelInfo(
        'sdxl-turbo',
        '',
        ModelTypeConst.TTI,
        xinference_tti_model_credential,
        XinferenceTextToImage
    ),
    ModelInfo(
        'stable-diffusion-v1.5',
        '',
        ModelTypeConst.TTI,
        xinference_tti_model_credential,
        XinferenceTextToImage
    ),
    ModelInfo(
        'stable-diffusion-xl-base-1.0',
        '',
        ModelTypeConst.TTI,
        xinference_tti_model_credential,
        XinferenceTextToImage
    ),
    ModelInfo(
        'sd3-medium',
        '',
        ModelTypeConst.TTI,
        xinference_tti_model_credential,
        XinferenceTextToImage
    ),
    ModelInfo(
        'FLUX.1-schnell',
        '',
        ModelTypeConst.TTI,
        xinference_tti_model_credential,
        XinferenceTextToImage
    ),
    ModelInfo(
        'FLUX.1-dev',
        '',
        ModelTypeConst.TTI,
        xinference_tti_model_credential,
        XinferenceTextToImage
    ),
]

xinference_embedding_model_credential = XinferenceEmbeddingModelCredential()

# 生成embedding_model_info列表
embedding_model_info = [
    ModelInfo('bce-embedding-base_v1', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-base-en', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-base-en-v1.5', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-base-zh', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-base-zh-v1.5', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-large-en', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-large-en-v1.5', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-large-zh', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-large-zh-noinstruct', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-large-zh-v1.5', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-m3', '', ModelTypeConst.EMBEDDING, xinference_embedding_model_credential,
              XinferenceEmbedding),
    ModelInfo('bge-small-en-v1.5', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-small-zh', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-small-zh-v1.5', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('e5-large-v2', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('gte-base', '', ModelTypeConst.EMBEDDING, xinference_embedding_model_credential,
              XinferenceEmbedding),
    ModelInfo('gte-large', '', ModelTypeConst.EMBEDDING, xinference_embedding_model_credential,
              XinferenceEmbedding),
    ModelInfo('jina-embeddings-v2-base-en', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('jina-embeddings-v2-base-zh', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('jina-embeddings-v2-small-en', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('m3e-base', '', ModelTypeConst.EMBEDDING, xinference_embedding_model_credential,
              XinferenceEmbedding),
    ModelInfo('m3e-large', '', ModelTypeConst.EMBEDDING, xinference_embedding_model_credential,
              XinferenceEmbedding),
    ModelInfo('m3e-small', '', ModelTypeConst.EMBEDDING, xinference_embedding_model_credential,
              XinferenceEmbedding),
    ModelInfo('multilingual-e5-large', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('text2vec-base-chinese', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('text2vec-base-chinese-paraphrase', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('text2vec-base-chinese-sentence', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('text2vec-base-multilingual', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('text2vec-large-chinese', '', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
]
rerank_list = [ModelInfo('bce-reranker-base_v1',
                         '',
                         ModelTypeConst.RERANKER, XInferenceRerankerModelCredential(), XInferenceReranker)]
model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_model_info_list(voice_model_info)
    .append_default_model_info(voice_model_info[0])
    .append_default_model_info(voice_model_info[1])
    .append_default_model_info(ModelInfo('phi3',
                                         '',
                                         ModelTypeConst.LLM, xinference_llm_model_credential,
                                         XinferenceChatModel))
    .append_model_info_list(embedding_model_info)
    .append_default_model_info(ModelInfo('',
                                         '',
                                         ModelTypeConst.EMBEDDING,
                                         xinference_embedding_model_credential, XinferenceEmbedding))
    .append_model_info_list(rerank_list)
    .append_model_info_list(image_model_info)
    .append_default_model_info(image_model_info[0])
    .append_model_info_list(tti_model_info)
    .append_default_model_info(tti_model_info[0])
    .append_default_model_info(rerank_list[0])
    .build()
)


def get_base_url(url: str):
    parse = urlparse(url)
    result_url = ParseResult(scheme=parse.scheme, netloc=parse.netloc, path=parse.path, params='',
                             query='',
                             fragment='').geturl()
    return result_url[:-1] if result_url.endswith("/") else result_url


class XinferenceModelProvider(IModelProvider):
    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_xinference_provider', name='Xorbits Inference', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'xinference_model_provider', 'icon',
                         'xinference_icon_svg')))

    @staticmethod
    def get_base_model_list(api_base, api_key, model_type):
        base_url = get_base_url(api_base)
        base_url = base_url if base_url.endswith('/v1') else (base_url + '/v1')
        headers = {}
        if api_key:
            headers['Authorization'] = f"Bearer {api_key}"
        r = requests.request(method="GET", url=f"{base_url}/models", headers=headers, timeout=5)
        r.raise_for_status()
        model_list = r.json().get('data')
        return [model for model in model_list if model.get('model_type') == model_type]

    @staticmethod
    def get_model_info_by_name(model_list, model_name):
        if model_list is None:
            return []
        return [model for model in model_list if model.get('model_name') == model_name or model.get('id') == model_name]
