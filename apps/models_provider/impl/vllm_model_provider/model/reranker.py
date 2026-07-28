from typing import Sequence, Optional, Dict, Any

import cohere
from langchain_core.callbacks import Callbacks
from langchain_core.documents import BaseDocumentCompressor, Document

from models_provider.base_model_provider import MaxKBBaseModel


class VllmBgeReranker(MaxKBBaseModel, BaseDocumentCompressor):
    api_key: str
    api_url: str
    model: str
    top_n: Optional[int] = 3
    params: dict
    client: Any = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.model = kwargs.get('model')
        self.params = dict(kwargs.get('params') or {})
        self.api_url = kwargs.get('api_url')
        self.top_n = kwargs.get('top_n', 3)
        self.params.pop('top_n', None)
        self.client = cohere.Client(kwargs.get('api_key'), base_url=kwargs.get('api_url'))

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        r_url = model_credential.get('api_url')[:-3] if model_credential.get('api_url').endswith('/v1') else model_credential.get('api_url')
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        top_n = optional_params.pop('top_n', 3)
        return VllmBgeReranker(
            model=model_name,
            api_key=model_credential.get('api_key'),
            api_url=r_url,
            top_n=top_n,
            params=optional_params,
        )

    def compress_documents(self, documents: Sequence[Document], query: str, callbacks: Optional[Callbacks] = None) -> \
            Sequence[Document]:
        if documents is None or len(documents) == 0:
            return []

        ds = [d.page_content for d in documents]
        try:
            result = self.client.v2.rerank(model=self.model, query=query, documents=ds, top_n=self.top_n)
        except cohere.NotFoundError:
            result = self.client.rerank(model=self.model, query=query, documents=ds, top_n=self.top_n)

        reranked_documents = []
        for item in result.results:
            if item.index < 0 or item.index >= len(documents):
                raise ValueError(f'Rerank result index {item.index} is out of range')
            source = documents[item.index]
            reranked_documents.append(
                Document(
                    page_content=source.page_content,
                    metadata={**source.metadata, 'relevance_score': item.relevance_score},
                )
            )
        return reranked_documents
