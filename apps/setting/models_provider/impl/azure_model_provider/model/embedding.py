# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/7/12 17:44
    @desc:
"""
from typing import Dict

from langchain_openai import AzureOpenAIEmbeddings

from setting.models_provider.base_model_provider import MaxKBBaseModel


class AzureOpenAIEmbeddingModel(MaxKBBaseModel, AzureOpenAIEmbeddings):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return AzureOpenAIEmbeddingModel(
            model=model_name,
            openai_api_key=model_credential.get('api_key'),
            azure_endpoint=model_credential.get('api_base'),
            openai_api_version=model_credential.get('api_version'),
            openai_api_type="azure",
        )
