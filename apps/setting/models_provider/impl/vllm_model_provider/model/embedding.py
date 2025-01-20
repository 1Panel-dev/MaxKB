# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/7/12 17:44
    @desc:
"""
from typing import Dict

from langchain_community.embeddings import OpenAIEmbeddings

from setting.models_provider.base_model_provider import MaxKBBaseModel


class VllmEmbeddingModel(MaxKBBaseModel, OpenAIEmbeddings):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return VllmEmbeddingModel(
            model=model_name,
            openai_api_key=model_credential.get('api_key'),
            openai_api_base=model_credential.get('api_base'),
        )
