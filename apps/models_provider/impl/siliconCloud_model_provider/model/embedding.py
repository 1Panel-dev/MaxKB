# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： embedding.py
@date：2024/10/16 16:34
@desc:
"""

from typing import Dict

import requests

from models_provider.base_model_provider import MaxKBBaseEmbeddingModel


class SiliconCloudEmbeddingModel(MaxKBBaseEmbeddingModel):
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
    def _is_multimodal(model_name: str) -> bool:
        """判断模型是否为支持图片向量的多模态模型。"""
        model_name = model_name.lower()
        return any(k in model_name for k in ("vl-embedding", "embedding-vision", "multimodal"))

    def supports_image_embedding(self) -> bool:
        return self._is_multimodal(self.model_name)

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseEmbeddingModel.filter_optional_params(model_kwargs)
        return SiliconCloudEmbeddingModel(
            api_key=model_credential.get("api_key"),
            model_name=model_name,
            optional_params=optional_params,
            base_url=model_credential.get("api_base"),
        )

    def _embed_input(self, content: str | dict) -> list[float]:
        payload = {"model": self.model_name, "input": content, **self.optional_params}
        headers = {"Authorization": f"Bearer {self.openai_api_key}", "Content-Type": "application/json"}

        response = requests.post(
            self.base_url.rstrip("/") + "/embeddings", json=payload, headers=headers, timeout=(10, 60)
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict) or "code" in data or not data.get("data"):
            raise ValueError("Embedding API returned no data")
        return data["data"][0]["embedding"]

    def embed_query(self, text: str) -> list:
        return self._embed_input(text)

    def embed_documents(self, texts: list) -> list:
        return [self.embed_query(text) for text in texts]

    def embed_images(self, images: list[str]) -> list[list[float]]:
        if not self.supports_image_embedding():
            return super().embed_images(images)
        # SiliconFlow /embeddings accepts one image content object per input.
        return [
            self._embed_input({"image": self.normalize_image_input(image, keep_data_prefix=True)}) for image in images
        ]
