# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： reranker.py.py
    @date：2024/9/2 16:42
    @desc:
"""
from typing import Sequence, Optional, Dict, Any

import requests
import torch
from langchain_core.callbacks import Callbacks
from langchain_core.documents import BaseDocumentCompressor, Document
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from setting.models_provider.base_model_provider import MaxKBBaseModel
from smartdoc.const import CONFIG


class LocalReranker(MaxKBBaseModel):
    def __init__(self, model_name, top_n=3, cache_dir=None):
        super().__init__()
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.top_n = top_n

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        if model_kwargs.get('use_local', True):
            return LocalBaseReranker(model_name=model_name, cache_dir=model_credential.get('cache_dir'),
                                     model_kwargs={'device': model_credential.get('device', 'cpu')}

                                     )
        return WebLocalBaseReranker(model_name=model_name, cache_dir=model_credential.get('cache_dir'),
                                    model_kwargs={'device': model_credential.get('device')},
                                    **model_kwargs)


class WebLocalBaseReranker(MaxKBBaseModel, BaseDocumentCompressor):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        pass

    model_id: str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model_id = kwargs.get('model_id', None)

    def compress_documents(self, documents: Sequence[Document], query: str, callbacks: Optional[Callbacks] = None) -> \
            Sequence[Document]:
        if documents is None or len(documents) == 0:
            return []
        bind = f'{CONFIG.get("LOCAL_MODEL_HOST")}:{CONFIG.get("LOCAL_MODEL_PORT")}'
        res = requests.post(
            f'{CONFIG.get("LOCAL_MODEL_PROTOCOL")}://{bind}/api/model/{self.model_id}/compress_documents',
            json={'documents': [{'page_content': document.page_content, 'metadata': document.metadata} for document in
                                documents], 'query': query}, headers={'Content-Type': 'application/json'})
        result = res.json()
        if result.get('code', 500) == 200:
            return [Document(page_content=document.get('page_content'), metadata=document.get('metadata')) for document
                    in result.get('data')]
        raise Exception(result.get('message'))


class LocalBaseReranker(MaxKBBaseModel, BaseDocumentCompressor):
    client: Any = None
    tokenizer: Any = None
    model: Optional[str] = None
    cache_dir: Optional[str] = None
    model_kwargs = {}

    def __init__(self, model_name, cache_dir=None, **model_kwargs):
        super().__init__()
        self.model = model_name
        self.cache_dir = cache_dir
        self.model_kwargs = model_kwargs
        self.client = AutoModelForSequenceClassification.from_pretrained(self.model, cache_dir=self.cache_dir)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model, cache_dir=self.cache_dir)
        self.client = self.client.to(self.model_kwargs.get('device', 'cpu'))
        self.client.eval()

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return LocalBaseReranker(model_name, cache_dir=model_credential.get('cache_dir'), **model_kwargs)

    def compress_documents(self, documents: Sequence[Document], query: str, callbacks: Optional[Callbacks] = None) -> \
            Sequence[Document]:
        if documents is None or len(documents) == 0:
            return []
        with torch.no_grad():
            inputs = self.tokenizer([[query, document.page_content] for document in documents], padding=True,
                                    truncation=True, return_tensors='pt', max_length=512)
            scores = [torch.sigmoid(s).float().item() for s in
                      self.client(**inputs, return_dict=True).logits.view(-1, ).float()]
            result = [Document(page_content=documents[index].page_content, metadata={'relevance_score': scores[index]})
                      for index
                      in range(len(documents))]
            result.sort(key=lambda row: row.metadata.get('relevance_score'), reverse=True)
            return result
