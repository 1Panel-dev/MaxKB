# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： aliyun_bai_lian_model_provider.py
    @date：2024/9/9 17:43
    @desc:
"""
import os

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import ModelProvideInfo, ModelTypeConst, ModelInfo, IModelProvider, \
    ModelInfoManage
from setting.models_provider.impl.aliyun_bai_lian_model_provider.credential.embedding import \
    AliyunBaiLianEmbeddingCredential
from setting.models_provider.impl.aliyun_bai_lian_model_provider.credential.llm import BaiLianLLMModelCredential
from setting.models_provider.impl.aliyun_bai_lian_model_provider.credential.reranker import \
    AliyunBaiLianRerankerCredential
from setting.models_provider.impl.aliyun_bai_lian_model_provider.credential.stt import AliyunBaiLianSTTModelCredential
from setting.models_provider.impl.aliyun_bai_lian_model_provider.credential.tts import AliyunBaiLianTTSModelCredential
from setting.models_provider.impl.aliyun_bai_lian_model_provider.model.embedding import AliyunBaiLianEmbedding
from setting.models_provider.impl.aliyun_bai_lian_model_provider.model.llm import BaiLianChatModel
from setting.models_provider.impl.aliyun_bai_lian_model_provider.model.reranker import AliyunBaiLianReranker
from setting.models_provider.impl.aliyun_bai_lian_model_provider.model.stt import AliyunBaiLianSpeechToText
from setting.models_provider.impl.aliyun_bai_lian_model_provider.model.tts import AliyunBaiLianTextToSpeech
from smartdoc.conf import PROJECT_DIR

aliyun_bai_lian_model_credential = AliyunBaiLianRerankerCredential()
aliyun_bai_lian_tts_model_credential = AliyunBaiLianTTSModelCredential()
aliyun_bai_lian_stt_model_credential = AliyunBaiLianSTTModelCredential()
aliyun_bai_lian_embedding_model_credential = AliyunBaiLianEmbeddingCredential()
aliyun_bai_lian_llm_model_credential = BaiLianLLMModelCredential()

model_info_list = [ModelInfo('gte-rerank',
                             '阿里巴巴通义实验室开发的GTE-Rerank文本排序系列模型，开发者可以通过LlamaIndex框架进行集成高质量文本检索、排序。',
                             ModelTypeConst.RERANKER, aliyun_bai_lian_model_credential, AliyunBaiLianReranker),
                   ModelInfo('paraformer-realtime-v2',
                             '中文（含粤语等各种方言）、英文、日语、韩语支持多个语种自由切换',
                             ModelTypeConst.STT, aliyun_bai_lian_stt_model_credential, AliyunBaiLianSpeechToText),
                   ModelInfo('cosyvoice-v1',
                             'CosyVoice基于新一代生成式语音大模型，能根据上下文预测情绪、语调、韵律等，具有更好的拟人效果',
                             ModelTypeConst.TTS, aliyun_bai_lian_tts_model_credential, AliyunBaiLianTextToSpeech),
                   ModelInfo('text-embedding-v1',
                             '通用文本向量，是通义实验室基于LLM底座的多语言文本统一向量模型，面向全球多个主流语种，提供高水准的向量服务，帮助开发者将文本数据快速转换为高质量的向量数据。',
                             ModelTypeConst.EMBEDDING, aliyun_bai_lian_embedding_model_credential,
                             AliyunBaiLianEmbedding),
                   ModelInfo('qwen-turbo', '', ModelTypeConst.LLM, aliyun_bai_lian_llm_model_credential,
                             BaiLianChatModel),
                   ModelInfo('qwen-plus', '', ModelTypeConst.LLM, aliyun_bai_lian_llm_model_credential,
                             BaiLianChatModel),
                   ModelInfo('qwen-max', '', ModelTypeConst.LLM, aliyun_bai_lian_llm_model_credential,
                             BaiLianChatModel)
                   ]

model_info_manage = ModelInfoManage.builder().append_model_info_list(model_info_list).append_default_model_info(
    model_info_list[1]).append_default_model_info(model_info_list[2]).append_default_model_info(
    model_info_list[3]).append_default_model_info(model_info_list[4]).build()


class AliyunBaiLianModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='aliyun_bai_lian_model_provider', name='阿里云百炼', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'aliyun_bai_lian_model_provider',
                         'icon',
                         'aliyun_bai_lian_icon_svg')))
