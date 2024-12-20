# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/7/12 17:44
    @desc:
"""
from typing import Dict

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from setting.models_provider.base_model_provider import MaxKBBaseModel


class GeminiEmbeddingModel(MaxKBBaseModel, GoogleGenerativeAIEmbeddings):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return GeminiEmbeddingModel(
            google_api_key=model_credential.get('api_key'),
            model=model_name,
        )
