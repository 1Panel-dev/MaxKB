# coding=utf-8

from typing import Dict, List

import requests

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseEmbeddingModel


class TencentEmbeddingModel(MaxKBBaseEmbeddingModel):
    """腾讯 TokenHub 向量模型（OpenAI Embeddings 兼容接口）。

    文本向量：POST /v1/embeddings
    多模态向量：POST /v1/embeddings/multimodal（kinfra-vl-embedding-* 支持文本、图片、视频）
    """

    DEFAULT_BASE_URL: str = "https://tokenhub.tencentmaas.com/v1"
    REQUEST_TIMEOUT: tuple = (10, 60)

    def __init__(self, api_key: str, model_name: str, base_url: str, params: dict = None):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.params = params or {}

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type: str, model_name: str, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseEmbeddingModel.filter_optional_params(model_kwargs)
        return TencentEmbeddingModel(
            api_key=model_credential.get("api_key"),
            model_name=model_name,
            base_url=model_credential.get("base_url") or TencentEmbeddingModel.DEFAULT_BASE_URL,
            params=optional_params,
        )

    def supports_image_embedding(self) -> bool:
        return "vl-embedding" in self.model_name

    def _embedding_url(self) -> str:
        if self.supports_image_embedding():
            return f"{self.base_url}/embeddings/multimodal"
        return f"{self.base_url}/embeddings"

    def _post(self, payload: dict) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        response = requests.post(self._embedding_url(), headers=headers, json=payload, timeout=self.REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _extract_embedding(result: dict) -> List[float]:
        data = result.get("data") or []
        if not data:
            maxkb_logger.error(f"Tencent TokenHub embedding returned no data: {result}")
            raise RuntimeError("Tencent TokenHub embedding API returned no embedding")
        return data[0].get("embedding", [])

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self.supports_image_embedding():
            # 多模态接口单次请求融合为一个向量，逐条处理
            return [self._embed_multimodal([{"type": "text", "text": text}]) for text in texts]
        payload = {"model": self.model_name, "input": texts, "encoding_format": "float", **self.params}
        result = self._post(payload)
        return [item.get("embedding", []) for item in result.get("data", [])]

    def embed_query(self, text: str) -> List[float]:
        if self.supports_image_embedding():
            return self._embed_multimodal([{"type": "text", "text": text}])
        payload = {"model": self.model_name, "input": text, "encoding_format": "float", **self.params}
        return self._extract_embedding(self._post(payload))

    def embed_images(self, images: List[str]) -> List[List[float]]:
        if not self.supports_image_embedding():
            return []
        return [
            self._embed_multimodal([{"type": "image_url", "image_url": {"url": self._to_base64_content(url)}}])
            for url in images
        ]

    @staticmethod
    def _to_base64_content(url: str) -> str:
        """TokenHub 的 image_url.url 接受 URL 或 base64 内容。

        MaxKB 传入的图片是 data:image/...;base64,xxx 形式的 data URL，
        这里剥掉 data: 前缀，转换为纯 base64 内容再交给接口。
        """
        return MaxKBBaseEmbeddingModel.normalize_image_input(url, keep_data_prefix=False)

    def _embed_multimodal(self, items: list) -> List[float]:
        payload = {"model": self.model_name, "input": items, "encoding_format": "float", **self.params}
        return self._extract_embedding(self._post(payload))
