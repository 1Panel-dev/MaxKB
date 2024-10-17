# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： wenxin_model_provider.py
    @date：2023/10/31 16:19
    @desc:
"""
import os

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import ModelProvideInfo, ModelTypeConst, ModelInfo, IModelProvider, \
    ModelInfoManage
from setting.models_provider.impl.wenxin_model_provider.credential.embedding import QianfanEmbeddingCredential
from setting.models_provider.impl.wenxin_model_provider.credential.llm import WenxinLLMModelCredential
from setting.models_provider.impl.wenxin_model_provider.model.embedding import QianfanEmbeddings
from setting.models_provider.impl.wenxin_model_provider.model.llm import QianfanChatModel
from smartdoc.conf import PROJECT_DIR

win_xin_llm_model_credential = WenxinLLMModelCredential()
qianfan_embedding_credential = QianfanEmbeddingCredential()
model_info_list = [ModelInfo('ERNIE-Bot-4',
                             'ERNIE-Bot-4是百度自行研发的大语言模型，覆盖海量中文数据，具有更强的对话问答、内容创作生成等能力。',
                             ModelTypeConst.LLM, win_xin_llm_model_credential, QianfanChatModel),
                   ModelInfo('ERNIE-Bot',
                             'ERNIE-Bot是百度自行研发的大语言模型，覆盖海量中文数据，具有更强的对话问答、内容创作生成等能力。',
                             ModelTypeConst.LLM, win_xin_llm_model_credential, QianfanChatModel),
                   ModelInfo('ERNIE-Bot-turbo',
                             'ERNIE-Bot-turbo是百度自行研发的大语言模型，覆盖海量中文数据，具有更强的对话问答、内容创作生成等能力，响应速度更快。',
                             ModelTypeConst.LLM, win_xin_llm_model_credential, QianfanChatModel),
                   ModelInfo('BLOOMZ-7B',
                             'BLOOMZ-7B是业内知名的大语言模型，由BigScience研发并开源，能够以46种语言和13种编程语言输出文本。',
                             ModelTypeConst.LLM, win_xin_llm_model_credential, QianfanChatModel),
                   ModelInfo('Llama-2-7b-chat',
                             'Llama-2-7b-chat由Meta AI研发并开源，在编码、推理及知识应用等场景表现优秀，Llama-2-7b-chat是高性能原生开源版本，适用于对话场景。',
                             ModelTypeConst.LLM, win_xin_llm_model_credential, QianfanChatModel),
                   ModelInfo('Llama-2-13b-chat',
                             'Llama-2-13b-chat由Meta AI研发并开源，在编码、推理及知识应用等场景表现优秀，Llama-2-13b-chat是性能与效果均衡的原生开源版本，适用于对话场景。',
                             ModelTypeConst.LLM, win_xin_llm_model_credential, QianfanChatModel),
                   ModelInfo('Llama-2-70b-chat',
                             'Llama-2-70b-chat由Meta AI研发并开源，在编码、推理及知识应用等场景表现优秀，Llama-2-70b-chat是高精度效果的原生开源版本。',
                             ModelTypeConst.LLM, win_xin_llm_model_credential, QianfanChatModel),
                   ModelInfo('Qianfan-Chinese-Llama-2-7B',
                             '千帆团队在Llama-2-7b基础上的中文增强版本，在CMMLU、C-EVAL等中文知识库上表现优异。',
                             ModelTypeConst.LLM, win_xin_llm_model_credential, QianfanChatModel)
                   ]
embedding_model_info = ModelInfo('Embedding-V1',
                                 'Embedding-V1是一个基于百度文心大模型技术的文本表示模型，可以将文本转化为用数值表示的向量形式，用于文本检索、信息推荐、知识挖掘等场景。 Embedding-V1提供了Embeddings接口，可以根据输入内容生成对应的向量表示。您可以通过调用该接口，将文本输入到模型中，获取到对应的向量表示，从而进行后续的文本处理和分析。',
                                 ModelTypeConst.EMBEDDING, qianfan_embedding_credential, QianfanEmbeddings)
model_info_manage = ModelInfoManage.builder().append_model_info_list(model_info_list).append_default_model_info(
    ModelInfo('ERNIE-Bot-4',
              'ERNIE-Bot-4是百度自行研发的大语言模型，覆盖海量中文数据，具有更强的对话问答、内容创作生成等能力。',
              ModelTypeConst.LLM,
              win_xin_llm_model_credential,
              QianfanChatModel)).append_model_info(embedding_model_info).append_default_model_info(
    embedding_model_info).build()


class WenxinModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_wenxin_provider', name='千帆大模型', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'wenxin_model_provider', 'icon',
                         'azure_icon_svg')))
