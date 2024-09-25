# coding=utf-8
import os
from urllib.parse import urlparse, ParseResult

import requests

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, ModelTypeConst, \
    ModelInfoManage
from setting.models_provider.impl.xinference_model_provider.credential.embedding import \
    XinferenceEmbeddingModelCredential
from setting.models_provider.impl.xinference_model_provider.credential.llm import XinferenceLLMModelCredential
from setting.models_provider.impl.xinference_model_provider.credential.reranker import XInferenceRerankerModelCredential
from setting.models_provider.impl.xinference_model_provider.model.embedding import XinferenceEmbedding
from setting.models_provider.impl.xinference_model_provider.model.llm import XinferenceChatModel
from setting.models_provider.impl.xinference_model_provider.model.reranker import XInferenceReranker
from smartdoc.conf import PROJECT_DIR

xinference_llm_model_credential = XinferenceLLMModelCredential()
model_info_list = [
    ModelInfo(
        'code-llama',
        'Code Llama 是一个专门用于代码生成的语言模型。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'code-llama-instruct',
        'Code Llama Instruct 是 Code Llama 的指令微调版本，专为执行特定任务而设计。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'code-llama-python',
        'Code Llama Python 是一个专门用于 Python 代码生成的语言模型。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'codeqwen1.5',
        'CodeQwen 1.5 是一个用于代码生成的语言模型，具有较高的性能。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'codeqwen1.5-chat',
        'CodeQwen 1.5 Chat 是一个聊天模型版本的 CodeQwen 1.5。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'deepseek',
        'Deepseek 是一个大规模语言模型，具有 130 亿参数。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'deepseek-chat',
        'Deepseek Chat 是一个聊天模型版本的 Deepseek。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'deepseek-coder',
        'Deepseek Coder 是一个专为代码生成设计的模型。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'deepseek-coder-instruct',
        'Deepseek Coder Instruct 是 Deepseek Coder 的指令微调版本，专为执行特定任务而设计。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'deepseek-vl-chat',
        'Deepseek VL Chat 是 Deepseek 的视觉语言聊天模型版本，能够处理图像和文本输入。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'gpt-3.5-turbo',
        'GPT-3.5 Turbo 是一个高效能的通用语言模型，适用于多种应用场景。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'gpt-4',
        'GPT-4 是一个强大的多模态模型，不仅支持文本输入，还支持图像输入。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'gpt-4-vision-preview',
        'GPT-4 Vision Preview 是 GPT-4 的视觉预览版本，支持图像输入。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'gpt4all',
        'GPT4All 是一个开源的多模态模型，支持文本和图像输入。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'llama2',
        'Llama2 是一个具有 700 亿参数的大规模语言模型，支持多种语言。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'llama2-chat',
        'Llama2 Chat 是一个聊天模型版本的 Llama2，支持多种语言。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'llama2-chat-32k',
        'Llama2 Chat 32K 是一个聊天模型版本的 Llama2，支持长达 32K 令牌的上下文。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen',
        'Qwen 是一个大规模语言模型，具有 130 亿参数。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen-chat',
        'Qwen Chat 是一个聊天模型版本的 Qwen。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen-chat-32k',
        'Qwen Chat 32K 是一个聊天模型版本的 Qwen，支持长达 32K 令牌的上下文。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen-code',
        'Qwen Code 是一个专门用于代码生成的语言模型。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen-code-chat',
        'Qwen Code Chat 是一个聊天模型版本的 Qwen Code。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen-vl',
        'Qwen VL 是 Qwen 的视觉语言模型版本，能够处理图像和文本输入。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen-vl-chat',
        'Qwen VL Chat 是 Qwen VL 的聊天模型版本，能够处理图像和文本输入。',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
    ModelInfo(
        'qwen2-instruct',
        'Qwen2 Instruct 是 Qwen2 的指令微调版本，专为执行特定任务而设计。',
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
        'MiniCPM-Llama3-V 2.5是MiniCPM-V系列中的最新型号，该模型基于SigLip-400M和Llama3-8B-Instruct构建，共有8B个参数',
        ModelTypeConst.LLM,
        xinference_llm_model_credential,
        XinferenceChatModel
    ),
]

xinference_embedding_model_credential = XinferenceEmbeddingModelCredential()

# 生成embedding_model_info列表
embedding_model_info = [
    ModelInfo('bce-embedding-base_v1', 'BCE 嵌入模型的基础版本。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-base-en', 'BGE 英语基础版本的嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-base-en-v1.5', 'BGE 英语基础版本 1.5 的嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-base-zh', 'BGE 中文基础版本的嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-base-zh-v1.5', 'BGE 中文基础版本 1.5 的嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-large-en', 'BGE 英语大型版本的嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-large-en-v1.5', 'BGE 英语大型版本 1.5 的嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-large-zh', 'BGE 中文大型版本的嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-large-zh-noinstruct', 'BGE 中文大型版本的嵌入模型，无指令调整。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-large-zh-v1.5', 'BGE 中文大型版本 1.5 的嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-m3', 'BGE M3 版本的嵌入模型。', ModelTypeConst.EMBEDDING, xinference_embedding_model_credential,
              XinferenceEmbedding),
    ModelInfo('bge-small-en-v1.5', 'BGE 英语小型版本 1.5 的嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-small-zh', 'BGE 中文小型版本的嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('bge-small-zh-v1.5', 'BGE 中文小型版本 1.5 的嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('e5-large-v2', 'E5 大型版本 2 的嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('gte-base', 'GTE 基础版本的嵌入模型。', ModelTypeConst.EMBEDDING, xinference_embedding_model_credential,
              XinferenceEmbedding),
    ModelInfo('gte-large', 'GTE 大型版本的嵌入模型。', ModelTypeConst.EMBEDDING, xinference_embedding_model_credential,
              XinferenceEmbedding),
    ModelInfo('jina-embeddings-v2-base-en', 'Jina 嵌入模型的英语基础版本 2。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('jina-embeddings-v2-base-zh', 'Jina 嵌入模型的中文基础版本 2。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('jina-embeddings-v2-small-en', 'Jina 嵌入模型的英语小型版本 2。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('m3e-base', 'M3E 基础版本的嵌入模型。', ModelTypeConst.EMBEDDING, xinference_embedding_model_credential,
              XinferenceEmbedding),
    ModelInfo('m3e-large', 'M3E 大型版本的嵌入模型。', ModelTypeConst.EMBEDDING, xinference_embedding_model_credential,
              XinferenceEmbedding),
    ModelInfo('m3e-small', 'M3E 小型版本的嵌入模型。', ModelTypeConst.EMBEDDING, xinference_embedding_model_credential,
              XinferenceEmbedding),
    ModelInfo('multilingual-e5-large', '多语言大型版本的 E5 嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('text2vec-base-chinese', 'Text2Vec 的中文基础版本嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('text2vec-base-chinese-paraphrase', 'Text2Vec 的中文基础版本的同义句嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('text2vec-base-chinese-sentence', 'Text2Vec 的中文基础版本的句子嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('text2vec-base-multilingual', 'Text2Vec 的多语言基础版本嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
    ModelInfo('text2vec-large-chinese', 'Text2Vec 的中文大型版本嵌入模型。', ModelTypeConst.EMBEDDING,
              xinference_embedding_model_credential, XinferenceEmbedding),
]
rerank_list = [ModelInfo('bce-reranker-base_v1',
                         '发布新的重新排名器，建立在强大的 M3 和LLM （GEMMA 和 MiniCPM，实际上没那么大）骨干上，支持多语言处理和更大的输入，大幅提高 BEIR、C-MTEB/Retrieval 的排名性能、MIRACL、LlamaIndex 评估',
                         ModelTypeConst.RERANKER, XInferenceRerankerModelCredential(), XInferenceReranker)]
model_info_manage = (ModelInfoManage.builder().append_model_info_list(model_info_list).append_default_model_info(
    ModelInfo(
        'phi3',
        'Phi-3 Mini是Microsoft的3.8B参数，轻量级，最先进的开放模型。',
        ModelTypeConst.LLM, xinference_llm_model_credential, XinferenceChatModel))
                     .append_model_info_list(
    embedding_model_info).append_default_model_info(
    ModelInfo(
        '',
        '',
        ModelTypeConst.EMBEDDING, xinference_embedding_model_credential, XinferenceEmbedding))
                     .append_model_info_list(rerank_list).append_default_model_info(rerank_list[0])
                     .build())


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
    def get_base_model_list(api_base, model_type):
        base_url = get_base_url(api_base)
        base_url = base_url if base_url.endswith('/v1') else (base_url + '/v1')
        r = requests.request(method="GET", url=f"{base_url}/models", timeout=5)
        r.raise_for_status()
        model_list = r.json().get('data')
        return [model for model in model_list if model.get('model_type') == model_type]

    @staticmethod
    def get_model_info_by_name(model_list, model_name):
        if model_list is None:
            return []
        return [model for model in model_list if model.get('model_name') == model_name]
