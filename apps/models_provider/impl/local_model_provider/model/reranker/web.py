# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： web.py
    @date：2025/11/5 15:30
    @desc:
"""
from typing import Sequence, Optional, Dict

import requests
from anthropic import BaseModel
from langchain_core.callbacks import Callbacks
from langchain_core.documents import Document, BaseDocumentCompressor

from maxkb.const import CONFIG
from models_provider.base_model_provider import MaxKBBaseModel


class LocalReranker(MaxKBBaseModel, BaseModel, BaseDocumentCompressor):

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return LocalReranker(model_type=model_type, model_name=model_name, model_credential=model_credential,
                             **model_kwargs)

    model_id: str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print('ssss', kwargs.get('model_id', None))
        self.model_id = kwargs.get('model_id', None)

    def compress_documents(self, documents: Sequence[Document], query: str, callbacks: Optional[Callbacks] = None) -> \
            Sequence[Document]:
        if documents is None or len(documents) == 0:
            return []
        prefix = CONFIG.get_admin_path()
        bind = f'{CONFIG.get("LOCAL_MODEL_HOST")}:{CONFIG.get("LOCAL_MODEL_PORT")}'
        res = requests.post(
            f'{CONFIG.get("LOCAL_MODEL_PROTOCOL")}://{bind}{prefix}/api/model/{self.model_id}/compress_documents',
            json={'documents': [{'page_content': document.page_content, 'metadata': document.metadata} for document in
                                documents], 'query': query}, headers={'Content-Type': 'application/json'})
        result = res.json()
        if result.get('code', 500) == 200:
            return [Document(page_content=document.get('page_content'), metadata=document.get('metadata')) for document
                    in result.get('data')]
        raise Exception(result.get('message'))
