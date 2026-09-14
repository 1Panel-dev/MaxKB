# coding=utf-8
"""
@project: maxkb
@Author：虎
@file： qianfan_model_provider.py
@date：2023/10/31 16:19
@desc:
"""

import os

from common.utils.common import get_file_content
from models_provider.base_model_provider import (
    ModelProvideInfo,
    ModelTypeConst,
    ModelInfo,
    IModelProvider,
    ModelInfoManage,
)
from models_provider.impl.qianfan_model_provider.credential.embedding import QianfanEmbeddingCredential
from models_provider.impl.qianfan_model_provider.credential.image import QianfanImageModelCredential
from models_provider.impl.qianfan_model_provider.credential.llm import QianfanLLMModelCredential
from models_provider.impl.qianfan_model_provider.credential.reranker import QfRerankerCredential
from models_provider.impl.qianfan_model_provider.credential.tti import QianfanTextToImageModelCredential
from models_provider.impl.qianfan_model_provider.credential.ttv import QianfanVideoModelCredential
from models_provider.impl.qianfan_model_provider.model.embedding import QianfanEmbeddings
from models_provider.impl.qianfan_model_provider.model.image import QianfanVisionModel
from models_provider.impl.qianfan_model_provider.model.llm import QianfanChatModel
from models_provider.impl.qianfan_model_provider.model.tti import QianfanTextToImage
from models_provider.impl.qianfan_model_provider.model.ttv import QianfanVideoModel
from maxkb.conf import PROJECT_DIR
from django.utils.translation import gettext as _

from models_provider.impl.qianfan_model_provider.model.reranker import QfBgeReranker

qianfan_llm_model_credential = QianfanLLMModelCredential()
qianfan_image_model_credential = QianfanImageModelCredential()
qianfan_tti_model_credential = QianfanTextToImageModelCredential()
qianfan_video_model_credential = QianfanVideoModelCredential()
qianfan_embedding_credential = QianfanEmbeddingCredential()
qf_reranker_credential = QfRerankerCredential()
model_info_list = [
    ModelInfo("ernie-5.1", "", ModelTypeConst.LLM, qianfan_llm_model_credential, QianfanChatModel),
    ModelInfo("ernie-5.0", "", ModelTypeConst.LLM, qianfan_llm_model_credential, QianfanChatModel),
    ModelInfo("ernie-4.5-turbo-128k", "", ModelTypeConst.LLM, qianfan_llm_model_credential, QianfanChatModel),
    ModelInfo("deepseek-v4-pro", "", ModelTypeConst.LLM, qianfan_llm_model_credential, QianfanChatModel),
    ModelInfo("ernie-4.5-turbo-32k", "", ModelTypeConst.LLM, qianfan_llm_model_credential, QianfanChatModel),
]
image_model_info_list = [
    ModelInfo("qwen2.5-vl-7b-instruct", "", ModelTypeConst.IMAGE, qianfan_image_model_credential, QianfanVisionModel),
    ModelInfo("ernie-4.5-vl-28b-a3b", "", ModelTypeConst.IMAGE, qianfan_image_model_credential, QianfanVisionModel),
]
tti_model_info_list = [
    ModelInfo("musesteamer-air-image", "", ModelTypeConst.TTI, qianfan_tti_model_credential, QianfanTextToImage),
    ModelInfo("qwen-image", "", ModelTypeConst.TTI, qianfan_tti_model_credential, QianfanTextToImage),
    ModelInfo("ernie-image-turbo", "", ModelTypeConst.TTI, qianfan_tti_model_credential, QianfanTextToImage),
]
itv_model_info_list = [
    ModelInfo("musesteamer-air-i2v", "", ModelTypeConst.ITV, qianfan_video_model_credential, QianfanVideoModel),
]
embedding_model_info_list = [
    ModelInfo("Embedding-V1", "", ModelTypeConst.EMBEDDING, qianfan_embedding_credential, QianfanEmbeddings),
    ModelInfo("bge-large-zh", "", ModelTypeConst.EMBEDDING, qianfan_embedding_credential, QianfanEmbeddings),
]
rerank_model_info_list = [
    ModelInfo("bce-reranker-base", "", ModelTypeConst.RERANKER, qf_reranker_credential, QfBgeReranker),
]
model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_default_model_info(
        ModelInfo("ernie-5.1", "", ModelTypeConst.LLM, qianfan_llm_model_credential, QianfanChatModel)
    )
    .append_model_info_list(image_model_info_list)
    .append_default_model_info(image_model_info_list[0])
    .append_model_info_list(tti_model_info_list)
    .append_default_model_info(tti_model_info_list[0])
    .append_model_info_list(itv_model_info_list)
    .append_default_model_info(itv_model_info_list[0])
    .append_model_info_list(embedding_model_info_list)
    .append_default_model_info(embedding_model_info_list[0])
    .append_model_info_list(rerank_model_info_list)
    .append_default_model_info(rerank_model_info_list[0])
    .build()
)


class QianfanModelProvider(IModelProvider):
    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(
            provider="model_qianfan_provider",
            name=_("Thousand sails large model"),
            icon=get_file_content(
                os.path.join(
                    PROJECT_DIR, "apps", "models_provider", "impl", "qianfan_model_provider", "icon", "qianfan_icon_svg"
                )
            ),
        )
