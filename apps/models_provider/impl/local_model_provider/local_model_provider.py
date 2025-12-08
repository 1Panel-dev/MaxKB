# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： zhipu_model_provider.py
    @date：2024/04/19 13:5
    @desc:
"""
import os

from django.utils.translation import gettext as _

from common.utils.common import get_file_content
from maxkb.conf import PROJECT_DIR
from models_provider.base_model_provider import ModelProvideInfo, ModelTypeConst, ModelInfo, IModelProvider, \
    ModelInfoManage
from models_provider.impl.local_model_provider.credential.embedding import LocalEmbeddingCredential
from models_provider.impl.local_model_provider.credential.reranker import LocalRerankerCredential
from models_provider.impl.local_model_provider.model.embedding import LocalEmbedding
from models_provider.impl.local_model_provider.model.reranker import LocalReranker

embedding_text2vec_base_chinese = ModelInfo('shibing624/text2vec-base-chinese', '', ModelTypeConst.EMBEDDING,
                                            LocalEmbeddingCredential(), LocalEmbedding)
bge_reranker_v2_m3 = ModelInfo('BAAI/bge-reranker-v2-m3', '', ModelTypeConst.RERANKER,
                               LocalRerankerCredential(), LocalReranker)

model_info_manage = (ModelInfoManage.builder().append_model_info(embedding_text2vec_base_chinese)
                     .append_default_model_info(embedding_text2vec_base_chinese)
                     .append_model_info(bge_reranker_v2_m3)
                     .append_default_model_info(bge_reranker_v2_m3)
                     .build())


class LocalModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_local_provider', name=_('local model'), icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", 'models_provider', 'impl', 'local_model_provider', 'icon',
                         'local_icon_svg')))
