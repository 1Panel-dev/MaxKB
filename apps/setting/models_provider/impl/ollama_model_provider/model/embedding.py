# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/7/12 15:02
    @desc:
"""
from typing import Dict

from langchain_community.embeddings import OllamaEmbeddings

from setting.models_provider.base_model_provider import MaxKBBaseModel


class OllamaEmbedding(MaxKBBaseModel, OllamaEmbeddings):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return OllamaEmbeddings(
            model=model_name,
            base_url=model_credential.get('api_base'),
        )
