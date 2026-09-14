# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： embedding.py
@date：2024/10/17 16:48
@desc:
"""

from typing import Dict, List

import openai

from models_provider.base_model_provider import MaxKBBaseEmbeddingModel


class QianfanEmbeddings(MaxKBBaseEmbeddingModel):
    """千帆 OpenAI 兼容向量接口（v2）"""

    model_name: str

    def supports_image_embedding(self) -> bool:
        return False

    @staticmethod
    def is_cache_model():
        return False

    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url).embeddings
        self.model_name = model_name

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return QianfanEmbeddings(
            api_key=model_credential.get("api_key"),
            model_name=model_name,
            base_url=model_credential.get("api_base"),
        )

    def embed_query(self, text: str):
        res = self.embed_documents([text])
        return res[0]

    def embed_documents(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        res = self.client.create(input=texts, model=self.model_name, encoding_format="float")
        return [e.embedding for e in res.data]
