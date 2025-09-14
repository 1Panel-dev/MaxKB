# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/10/17 16:48
    @desc:
"""
from typing import Dict, List
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
import openai
from models_provider.base_model_provider import MaxKBBaseModel


class QianfanV1Embeddings(MaxKBBaseModel, QianfanEmbeddingsEndpoint):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return QianfanV1Embeddings(
            model=model_name,
            qianfan_ak=model_credential.get('qianfan_ak'),
            qianfan_sk=model_credential.get('qianfan_sk'),
        )


class QianfanV2EmbeddingModel(MaxKBBaseModel):
    model_name: str

    @staticmethod
    def is_cache_model():
        return False

    def __init__(self, api_key, base_url, model_name: str):
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url).embeddings
        self.model_name = model_name

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return QianfanV2EmbeddingModel(
            api_key=model_credential.get('qianfan_ak'),
            model_name=model_name,
            base_url=model_credential.get('api_base'),
        )

    def embed_query(self, text: str):
        res = self.embed_documents([text])
        return res[0]

    def embed_documents(
            self, texts: List[ str],
    ) -> List[List[float]]:
        res = self.client.create(input=texts, model=self.model_name, encoding_format="float")
        return [e.embedding for e in res.data]


class QianfanEmbeddings(MaxKBBaseModel):


    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        api_version = model_credential.get('api_version', 'v1')

        if api_version == "v1":
            return QianfanV1Embeddings.new_instance(model_type, model_name, model_credential, **model_kwargs)
        elif api_version == "v2":
            return QianfanV2EmbeddingModel.new_instance(model_type, model_name, model_credential, **model_kwargs)
