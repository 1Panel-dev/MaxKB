# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： web.py
    @date：2025/11/5 15:24
    @desc:
"""

from typing import Dict, List

import requests
from anthropic import BaseModel
from langchain_core.embeddings import Embeddings

from maxkb.const import CONFIG
from models_provider.base_model_provider import MaxKBBaseModel


class LocalEmbedding(MaxKBBaseModel, BaseModel, Embeddings):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model_id = kwargs.get('model_id', None)

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return LocalEmbedding(model_name=model_name, cache_folder=model_credential.get('cache_folder'),
                              model_kwargs={'device': model_credential.get('device')},
                              encode_kwargs={'normalize_embeddings': True},
                              **model_kwargs)

    model_id: str = None

    def embed_query(self, text: str) -> List[float]:
        bind = f'{CONFIG.get("LOCAL_MODEL_HOST")}:{CONFIG.get("LOCAL_MODEL_PORT")}'
        prefix = CONFIG.get_admin_path()
        res = requests.post(
            f'{CONFIG.get("LOCAL_MODEL_PROTOCOL")}://{bind}{prefix}/api/model/{self.model_id}/embed_query',
            {'text': text})
        result = res.json()
        if result.get('code', 500) == 200:
            return result.get('data')
        raise Exception(result.get('message'))

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        bind = f'{CONFIG.get("LOCAL_MODEL_HOST")}:{CONFIG.get("LOCAL_MODEL_PORT")}'
        prefix = CONFIG.get_admin_path()
        res = requests.post(
            f'{CONFIG.get("LOCAL_MODEL_PROTOCOL")}://{bind}/{prefix}/api/model/{self.model_id}/embed_documents',
            {'texts': texts})
        result = res.json()
        if result.get('code', 500) == 200:
            return result.get('data')
        raise Exception(result.get('message'))
