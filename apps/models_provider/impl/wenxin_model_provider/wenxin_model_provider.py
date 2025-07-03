# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： wenxin_model_provider.py
    @date：2023/10/31 16:19
    @desc:
"""
import os

from common.utils.common import get_file_content
from models_provider.base_model_provider import ModelProvideInfo, ModelTypeConst, ModelInfo, IModelProvider, \
    ModelInfoManage
from models_provider.impl.wenxin_model_provider.credential.embedding import QianfanEmbeddingCredential
from models_provider.impl.wenxin_model_provider.credential.llm import WenxinLLMModelCredential
from models_provider.impl.wenxin_model_provider.model.embedding import QianfanEmbeddings
from models_provider.impl.wenxin_model_provider.model.llm import QianfanChatModel
from maxkb.conf import PROJECT_DIR
from django.utils.translation import gettext as _

win_xin_llm_model_credential = WenxinLLMModelCredential()
qianfan_embedding_credential = QianfanEmbeddingCredential()
model_info_list = [ModelInfo('ERNIE-Bot-4',
                             _('ERNIE-Bot-4 is a large language model independently developed by Baidu. It covers massive Chinese data and has stronger capabilities in dialogue Q&A, content creation and generation.'),
                             ModelTypeConst.LLM, win_xin_llm_model_credential, QianfanChatModel),
                   ModelInfo('ERNIE-Bot',
                             _('ERNIE-Bot is a large language model independently developed by Baidu. It covers massive Chinese data and has stronger capabilities in dialogue Q&A, content creation and generation.'),
                             ModelTypeConst.LLM, win_xin_llm_model_credential, QianfanChatModel),
                   ModelInfo('ERNIE-Bot-turbo',
                             _('ERNIE-Bot-turbo is a large language model independently developed by Baidu. It covers massive Chinese data, has stronger capabilities in dialogue Q&A, content creation and generation, and has a faster response speed.'),
                             ModelTypeConst.LLM, win_xin_llm_model_credential, QianfanChatModel),
                   ModelInfo('qianfan-chinese-llama-2-13b',
                             '',
                             ModelTypeConst.LLM, win_xin_llm_model_credential, QianfanChatModel)

                   ]
embedding_model_info = ModelInfo('Embedding-V1',
                                 _('Embedding-V1 is a text representation model based on Baidu Wenxin large model technology. It can convert text into a vector form represented by numerical values and can be used in text retrieval, information recommendation, knowledge mining and other scenarios. Embedding-V1 provides the Embeddings interface, which can generate corresponding vector representations based on input content. You can call this interface to input text into the model and obtain the corresponding vector representation for subsequent text processing and analysis.'),
                                 ModelTypeConst.EMBEDDING, qianfan_embedding_credential, QianfanEmbeddings)
model_info_manage = ModelInfoManage.builder().append_model_info_list(model_info_list).append_default_model_info(
    ModelInfo('ERNIE-Bot-4',
              _('ERNIE-Bot-4 is a large language model independently developed by Baidu. It covers massive Chinese data and has stronger capabilities in dialogue Q&A, content creation and generation.'),
              ModelTypeConst.LLM,
              win_xin_llm_model_credential,
              QianfanChatModel)).append_model_info(embedding_model_info).append_default_model_info(
    embedding_model_info).build()


class WenxinModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_wenxin_provider', name=_('Thousand sails large model'),
                                icon=get_file_content(
                                    os.path.join(PROJECT_DIR, "apps", 'models_provider', 'impl',
                                                 'wenxin_model_provider', 'icon',
                                                 'azure_icon_svg')))
