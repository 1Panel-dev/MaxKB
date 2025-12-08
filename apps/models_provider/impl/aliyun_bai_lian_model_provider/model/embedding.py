# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/10/16 16:34
    @desc:
"""
from typing import Dict, List

from openai import OpenAI

from models_provider.base_model_provider import MaxKBBaseModel


class AliyunBaiLianEmbedding(MaxKBBaseModel):
    model_name: str
    optional_params: dict

    def __init__(self, api_key, model_name: str, optional_params: dict):
        self.client = OpenAI(api_key=api_key, base_url='https://dashscope.aliyuncs.com/compatible-mode/v1').embeddings
        self.model_name = model_name
        self.optional_params = optional_params

    def is_cache_model(self):
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return AliyunBaiLianEmbedding(
            api_key=model_credential.get('dashscope_api_key'),
            model_name=model_name,
            optional_params=optional_params
        )

    def embed_query(self, text: str):
        res = self.embed_documents([text])
        return res[0]

    def embed_documents(
            self, texts: List[str], chunk_size: int | None = None
    ) -> List[List[float]]:
        if len(self.optional_params) > 0:
            res = self.client.create(
                input=texts, model=self.model_name, encoding_format="float",
                **self.optional_params
            )
        else:
            res = self.client.create(input=texts, model=self.model_name, encoding_format="float")
        return [e.embedding for e in res.data]
