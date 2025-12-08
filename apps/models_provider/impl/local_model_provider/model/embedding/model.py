# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： model.py
    @date：2025/11/5 15:26
    @desc:
"""
from typing import Dict

from langchain_huggingface import HuggingFaceEmbeddings

from models_provider.base_model_provider import MaxKBBaseModel


class LocalEmbedding(MaxKBBaseModel, HuggingFaceEmbeddings):
    @staticmethod
    def is_cache_model():
        return True

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return LocalEmbedding(model_name=model_name, cache_folder=model_credential.get('cache_folder'),
                              model_kwargs={'device': model_credential.get('device')},
                              encode_kwargs={'normalize_embeddings': True}
                              )
