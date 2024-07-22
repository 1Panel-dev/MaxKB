# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： zhipu_model_provider.py
    @date：2024/04/19 13:5
    @desc:
"""
import os
from typing import Dict

from pydantic import BaseModel

from common.exception.app_exception import AppApiException
from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import ModelProvideInfo, ModelTypeConst, ModelInfo, IModelProvider, \
    ModelInfoManage
from setting.models_provider.impl.local_model_provider.credential.embedding import LocalEmbeddingCredential
from setting.models_provider.impl.local_model_provider.model.embedding import LocalEmbedding
from smartdoc.conf import PROJECT_DIR

embedding_text2vec_base_chinese = ModelInfo('shibing624/text2vec-base-chinese', '', ModelTypeConst.EMBEDDING,
                                            LocalEmbeddingCredential(), LocalEmbedding)

model_info_manage = (ModelInfoManage.builder().append_model_info(embedding_text2vec_base_chinese)
                     .append_default_model_info(embedding_text2vec_base_chinese)
                     .build())


class LocalModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_local_provider', name='本地模型', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'local_model_provider', 'icon',
                         'local_icon_svg')))
