# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： embedding.py
@date：2024/10/16 16:34
@desc:
"""

from typing import Dict
from common.utils.logger import maxkb_logger
import requests

from models_provider.base_model_provider import MaxKBBaseModel


class SiliconCloudEmbeddingModel(MaxKBBaseModel):
    model_name: str
    openai_api_key: str
    base_url: str
    optional_params: dict

    def __init__(self, api_key, model_name: str, base_url, optional_params: dict):
        self.openai_api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.optional_params = optional_params

    def is_cache_model(self):
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return SiliconCloudEmbeddingModel(
            api_key=model_credential.get("api_key"),
            model_name=model_name,
            optional_params=optional_params,
            base_url=model_credential.get("api_base"),
        )

    def embed_query(self, text: str) -> list:
        payload = {"model": self.model_name, "input": text, **self.optional_params}
        headers = {"Authorization": f"Bearer {self.openai_api_key}", "Content-Type": "application/json"}

        response = requests.post(self.base_url + "/embeddings", json=payload, headers=headers)
        data = response.json()
        if isinstance(data, dict):
            if data["data"] is None or "code" in data:
                raise ValueError(f"Embedding API returned no data: {data}")
            # 假设返回结构中有 'data[0].embedding'
            return data["data"][0]["embedding"]
        else:
            maxkb_logger.error(f"Unexpected response from Embedding API: {data}")

    def embed_documents(self, texts: list) -> list:
        return [self.embed_query(text) for text in texts]
