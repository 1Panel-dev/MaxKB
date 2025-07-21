# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/7/12 17:44
    @desc:
"""
from typing import Dict

import requests
from langchain_community.embeddings import OpenAIEmbeddings

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel


class SiliconCloudEmbeddingModel(MaxKBBaseModel, OpenAIEmbeddings):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return SiliconCloudEmbeddingModel(
            openai_api_key=model_credential.get('api_key'),
            model=model_name,
            openai_api_base=model_credential.get('api_base'),
        )

    def embed_query(self, text: str) -> list:
        payload = {
            "model": self.model,
            "input": text
        }
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(self.openai_api_base + '/embeddings', json=payload, headers=headers)
        data = response.json()
        # print(data)
        if data['data'] is None or 'code' in data:
            raise ValueError(f"Embedding API returned no data: {data}")
        # 假设返回结构中有 'data[0].embedding'
        return data["data"][0]["embedding"]

    def embed_documents(self, texts: list) -> list:
        return [self.embed_query(text) for text in texts]
