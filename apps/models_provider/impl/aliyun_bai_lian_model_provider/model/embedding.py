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

from openai import OpenAI

from models_provider.base_model_provider import MaxKBBaseModel


class AliyunBaiLianEmbedding(MaxKBBaseModel):
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
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return AliyunBaiLianEmbedding(
            api_key=model_credential.get('dashscope_api_key'),
            model_name=model_name,
            api_base=model_credential.get('api_base') or 'https://dashscope.aliyuncs.com/compatible-mode/v1',
            optional_params=optional_params
        )

    def embed_query(self, text: str):
        res = self.embed_documents([text])
        return res[0]

    def embed_documents(
            self, texts: List[str], chunk_size: int | None = None
    ) -> List[List[float]]:
        # 处理多模态的向量化
        if any(k in self.model_name for k in ("vl-embedding", "embedding-vision", "multimodal")):
            import dashscope
            dashscope.api_key = self.api_key
            dashscope.base_http_api_url = self.api_base
            multimodal_input = [{"text": text} for text in texts]
            resp = dashscope.MultiModalEmbedding.call(
                model=self.model_name,
                input=multimodal_input,  # type: ignore
                **self.optional_params
            )

            if resp.status_code == HTTPStatus.OK:
                embeddings_data = resp.output.get('embeddings', [])
                return [item.get('embedding', []) for item in embeddings_data]
            else:
                raise Exception(f'MultiModalEmbedding call failed: status={resp.status_code}, message={resp.message}')

        if len(self.optional_params) > 0:
            res = self.client.create(
                input=texts, model=self.model_name, encoding_format="float",
                **self.optional_params
            )
        else:
            res = self.client.create(input=texts, model=self.model_name, encoding_format="float")
        return [e.embedding for e in res.data]
