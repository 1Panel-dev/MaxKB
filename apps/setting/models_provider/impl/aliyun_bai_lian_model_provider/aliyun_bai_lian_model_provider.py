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
from setting.models_provider.impl.aliyun_bai_lian_model_provider.credential.reranker import \
    AliyunBaiLianRerankerCredential
from setting.models_provider.impl.aliyun_bai_lian_model_provider.model.reranker import AliyunBaiLianReranker
from smartdoc.conf import PROJECT_DIR

aliyun_bai_lian_model_credential = AliyunBaiLianRerankerCredential()
model_info_list = [ModelInfo('gte-rerank',
                             '阿里巴巴通义实验室开发的GTE-Rerank文本排序系列模型，开发者可以通过LlamaIndex框架进行集成高质量文本检索、排序。',
                             ModelTypeConst.RERANKER, aliyun_bai_lian_model_credential, AliyunBaiLianReranker)
                   ]

model_info_manage = ModelInfoManage.builder().append_model_info_list(model_info_list).build()


class AliyunBaiLianModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='aliyun_bai_lian_model_provider', name='阿里云百炼', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'aliyun_bai_lian_model_provider',
                         'icon',
                         'aliyun_bai_lian_icon_svg')))
