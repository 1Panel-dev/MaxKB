# coding=utf-8
"""
    @project: MaxKB
    @file: embedding.py
    @desc: API Route Embedding Model
"""
from typing import Dict

from langchain_openai import OpenAIEmbeddings

from models_provider.base_model_provider import MaxKBBaseModel


class ApiRouteEmbeddingModel(MaxKBBaseModel, OpenAIEmbeddings):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return ApiRouteEmbeddingModel(
            api_key=model_credential.get('api_key'),
            model=model_name,
            openai_api_base=model_credential.get('api_base') or "https://global.api-route.com/v1",
        )
