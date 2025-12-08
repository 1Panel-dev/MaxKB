# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： model.py
    @date：2025/11/5 15:30
    @desc:
"""

from typing import Sequence, Optional, Dict, Any

from langchain_core.callbacks import Callbacks
from langchain_core.documents import Document, BaseDocumentCompressor

from models_provider.base_model_provider import MaxKBBaseModel


class LocalReranker(MaxKBBaseModel, BaseDocumentCompressor):
    client: Any = None
    tokenizer: Any = None
    model: Optional[str] = None
    cache_dir: Optional[str] = None
    model_kwargs: Any = {}

    def __init__(self, model_name, cache_dir=None, **model_kwargs):
        super().__init__()
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        self.model = model_name
        self.cache_dir = cache_dir
        self.model_kwargs = model_kwargs
        self.client = AutoModelForSequenceClassification.from_pretrained(self.model, cache_dir=self.cache_dir)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model, cache_dir=self.cache_dir)
        self.client = self.client.to(self.model_kwargs.get('device', 'cpu'))
        self.client.eval()

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return LocalReranker(model_name, cache_dir=model_credential.get('cache_dir'))

    def compress_documents(self, documents: Sequence[Document], query: str, callbacks: Optional[Callbacks] = None) -> \
            Sequence[Document]:
        if documents is None or len(documents) == 0:
            return []
        import torch
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
