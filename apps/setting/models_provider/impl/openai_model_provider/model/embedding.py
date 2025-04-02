# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/7/12 17:44
    @desc:
"""
from typing import Dict, List

import openai

from setting.models_provider.base_model_provider import MaxKBBaseModel


class OpenAIEmbeddingModel(MaxKBBaseModel):
    model_name: str

    def __init__(self, api_key, base_url, model_name: str):
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url).embeddings
        self.model_name = model_name

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return OpenAIEmbeddingModel(
            api_key=model_credential.get('api_key'),
            model_name=model_name,
            base_url=model_credential.get('api_base'),
        )

    def embed_query(self, text: str):
        res = self.embed_documents([text])
        return res[0]

    def embed_documents(
            self, texts: List[str], chunk_size: int | None = None
    ) -> List[List[float]]:
        res = self.client.create(input=texts, model=self.model_name, encoding_format="float")
        return [e.embedding for e in res.data]
