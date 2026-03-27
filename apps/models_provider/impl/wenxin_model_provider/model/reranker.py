import json
from typing import Sequence, Optional, Dict, Any

import requests
from langchain_core.callbacks import Callbacks
from langchain_core.documents import BaseDocumentCompressor, Document

from models_provider.base_model_provider import MaxKBBaseModel


class QfBgeReranker(MaxKBBaseModel, BaseDocumentCompressor):
    api_key: str
    api_url: str
    model: str
    params: dict
    top_n: int = 3

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.model = kwargs.get('model')
        self.params = kwargs.get('params', {})
        self.api_url = kwargs.get('api_url')
        self.top_n = self.params.get('top_n', 3)

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return QfBgeReranker(
            model=model_name,
            api_key=model_credential.get('api_key'),
            api_url=model_credential.get('api_url'),
            params=model_kwargs,
        )

    def compress_documents(
            self,
            documents: Sequence[Document],
            query: str,
            callbacks: Optional[Callbacks] = None
    ) -> Sequence[Document]:
        if not documents:
            return []

        texts = [doc.page_content for doc in documents]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        top_n = min(self.top_n, len(texts))
        payload = {
            "model": self.model,
            "query": query,
            "documents": texts,
            "top_n": top_n
        }

        response = requests.post(f"{self.api_url}/rerank", json=payload, headers=headers)

        if response.status_code != 200:
            raise RuntimeError(f"千帆 API 请求失败：{response.text}")

        res = response.json()

        return [
            Document(
                page_content=item.get('document', ''),
                metadata={'relevance_score': item.get('relevance_score')}
            )
            for item in res.get('results', [])
        ]
