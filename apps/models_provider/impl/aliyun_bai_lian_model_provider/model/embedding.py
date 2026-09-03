# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： embedding.py
@date：2024/10/16 16:34
@desc:
"""

from http import HTTPStatus
from typing import Dict, List

import dashscope
from openai import OpenAI

from models_provider.base_model_provider import MaxKBBaseEmbeddingModel


class AliyunBaiLianEmbedding(MaxKBBaseEmbeddingModel):
    model_name: str
    optional_params: dict
    api_base: str
    api_key: str

    def __init__(self, api_key, model_name: str, api_base: str, optional_params: dict):
        self.client = OpenAI(api_key=api_key, base_url=api_base).embeddings
        self.model_name = model_name
        self.optional_params = optional_params
        self.api_key = api_key
        self.api_base = api_base

    def is_cache_model(self):
        return False

    @staticmethod
    def _is_multimodal(model_name: str) -> bool:
        """判断模型是否为多模态向量模型（支持图片/视频独立向量）。"""
        return any(k in model_name for k in ("vl-embedding", "embedding-vision", "multimodal"))

    def supports_image_embedding(self) -> bool:
        return self._is_multimodal(self.model_name)

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseEmbeddingModel.filter_optional_params(model_kwargs)
        return AliyunBaiLianEmbedding(
            api_key=model_credential.get("dashscope_api_key"),
            model_name=model_name,
            api_base=model_credential.get("api_base") or "https://dashscope.aliyuncs.com/compatible-mode/v1",
            optional_params=optional_params,
        )

    def embed_query(self, text: str):
        res = self.embed_documents([text])
        return res[0]

    def embed_documents(self, texts: List[str], chunk_size: int | None = None) -> List[List[float]]:
        # 处理多模态的向量化
        if self._is_multimodal(self.model_name):
            return self._call_multimodal([{"text": text} for text in texts])

        if len(self.optional_params) > 0:
            res = self.client.create(
                input=texts, model=self.model_name, encoding_format="float", **self.optional_params
            )
        else:
            res = self.client.create(input=texts, model=self.model_name, encoding_format="float")
        return [e.embedding for e in res.data]

    def embed_images(self, images: List[str]) -> List[List[float]]:
        """对图片 URL / data URL 做独立向量化（每张图生成一个向量）。"""
        if not self.supports_image_embedding():
            return []
        return self._call_multimodal([{"image": image} for image in images])

    def _multimodal_base_url(self) -> str:
        """DashScope 原生多模态接口走 /api/v1，与 OpenAI 兼容地址区分开。"""
        base = self.api_base or "https://dashscope.aliyuncs.com/api/v1"
        if "/compatible-mode/" in base:
            return base.split("/compatible-mode/")[0] + "/api/v1"
        return base

    def _call_multimodal(self, items: List[dict]) -> List[List[float]]:
        dashscope.api_key = self.api_key
        dashscope.base_http_api_url = self._multimodal_base_url()
        resp = dashscope.MultiModalEmbedding.call(
            model=self.model_name,
            input=items,  # type: ignore
            **self.optional_params,
        )

        if resp.status_code == HTTPStatus.OK:
            embeddings_data = resp.output.get("embeddings", [])
            return [item.get("embedding", []) for item in embeddings_data]
        raise Exception(f"MultiModalEmbedding call failed: status={resp.status_code}, message={resp.message}")
