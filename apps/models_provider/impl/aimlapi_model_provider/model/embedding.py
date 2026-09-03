# coding=utf-8
"""
    @project: MaxKB
    @Author：aimlapi.com
    @file： embedding.py
    @date：2026/09/03 10:00
    @desc:
"""
from typing import Dict, List

import openai

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.aimlapi_model_provider.const import API_BASE, filter_optional_params, get_default_headers


class AIMLAPIEmbeddingModel(MaxKBBaseModel):
    model_name: str
    optional_params: dict

    def __init__(self, api_key, base_url, model_name: str, optional_params: dict):
        # 这里直接使用 openai SDK 下发字符串，而不是 langchain 的 OpenAIEmbeddings：
        # 后者会先把文本切成 token id 数组再发送，AI/ML API 的 /v1/embeddings 只接受字符串，
        # 收到 token id 数组会返回 400（details[].path = input）。
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url,
                                    default_headers=get_default_headers(base_url)).embeddings
        self.model_name = model_name
        self.optional_params = optional_params

    def is_cache_model(self):
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return AIMLAPIEmbeddingModel(
            api_key=model_credential.get('api_key'),
            model_name=model_name,
            base_url=model_credential.get('api_base') or API_BASE,
            optional_params=filter_optional_params(model_kwargs)
        )

    def embed_query(self, text: str):
        return self.embed_documents([text])[0]

    def embed_documents(self, texts: List[str], chunk_size: int | None = None) -> List[List[float]]:
        res = self.client.create(input=texts, model=self.model_name, encoding_format="float",
                                 **self.optional_params)
        return [e.embedding for e in res.data]
