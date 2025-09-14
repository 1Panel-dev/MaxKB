from typing import Sequence, Optional, Dict, Any

import cohere
from langchain_core.callbacks import Callbacks
from langchain_core.documents import BaseDocumentCompressor, Document

from models_provider.base_model_provider import MaxKBBaseModel


class VllmBgeReranker(MaxKBBaseModel, BaseDocumentCompressor):
    api_key: str
    api_url: str
    model: str
    params: dict
    client: Any = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.model = kwargs.get('model')
        self.params = kwargs.get('params')
        self.api_url = kwargs.get('api_url')
        self.client = cohere.ClientV2(kwargs.get('api_key'), base_url=kwargs.get('api_url'))

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        r_url = model_credential.get('api_url')[:-3] if model_credential.get('api_url').endswith('/v1') else model_credential.get('api_url')
        return VllmBgeReranker(
            model=model_name,
            api_key=model_credential.get('api_key'),
            api_url=r_url,
            params=model_kwargs,
            **model_kwargs
        )

    def compress_documents(self, documents: Sequence[Document], query: str, callbacks: Optional[Callbacks] = None) -> \
            Sequence[Document]:
        if documents is None or len(documents) == 0:
            return []

        ds = [d.page_content for d in documents]
        result = self.client.rerank(model=self.model, query=query, documents=ds)
        return [Document(page_content=d.document.get('text'), metadata={'relevance_score': d.relevance_score}) for d in
                result.results]
