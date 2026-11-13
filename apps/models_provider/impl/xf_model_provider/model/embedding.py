# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： embedding.py
@date：2026/11/13
@desc: Xunfei Spark 向量模型 OpenAI 兼容接口模型
"""

from typing import Dict, List

import openai

from models_provider.base_model_provider import MaxKBBaseEmbeddingModel


class XunFeiOpenAIEmbeddingModel(MaxKBBaseEmbeddingModel):
    def supports_image_embedding(self) -> bool:
        return False

    model_name: str
    optional_params: dict

    def __init__(self, api_key, base_url, model_name: str, optional_params: dict):
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url).embeddings
        self.model_name = model_name
        self.optional_params = optional_params

    def is_cache_model(self):
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseEmbeddingModel.filter_optional_params(model_kwargs)
        return XunFeiOpenAIEmbeddingModel(
            api_key=model_credential.get("api_key"),
            base_url=model_credential.get("api_base"),
            model_name=model_credential.get("model_id") or model_name,
            optional_params=optional_params,
        )

    def embed_query(self, text: str):
        res = self.embed_documents([text])
        return res[0]

    def embed_documents(self, texts: List[str], chunk_size: int | None = None) -> List[List[float]]:
        res = self.client.create(input=texts, model=self.model_name, encoding_format="float")
        return [e.embedding for e in res.data]
