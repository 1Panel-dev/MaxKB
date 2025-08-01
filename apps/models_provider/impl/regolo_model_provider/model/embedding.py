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

from models_provider.base_model_provider import MaxKBBaseModel


class RegoloEmbeddingModel(MaxKBBaseModel, OpenAIEmbeddings):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return RegoloEmbeddingModel(
            api_key=model_credential.get('api_key'),
            model=model_name,
            openai_api_base="https://api.regolo.ai/v1",
        )
