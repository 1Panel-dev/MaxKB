# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/10/17 16:48
    @desc:
"""
from typing import Dict

from langchain_community.embeddings import QianfanEmbeddingsEndpoint

from setting.models_provider.base_model_provider import MaxKBBaseModel


class QianfanEmbeddings(MaxKBBaseModel, QianfanEmbeddingsEndpoint):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return QianfanEmbeddings(
            model=model_name,
            qianfan_ak=model_credential.get('qianfan_ak'),
            qianfan_sk=model_credential.get('qianfan_sk'),
        )
