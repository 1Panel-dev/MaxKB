# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： reranker.py.py
    @date：2024/9/2 16:42
    @desc:
"""
from http import HTTPStatus
from typing import Sequence, Optional, Any, Dict

import dashscope
from langchain_core.callbacks import Callbacks
from langchain_core.documents import BaseDocumentCompressor, Document
from langchain_core.documents import BaseDocumentCompressor

from models_provider.base_model_provider import MaxKBBaseModel


class AliyunBaiLianReranker(MaxKBBaseModel, BaseDocumentCompressor):
    model: Optional[str]
    api_key: Optional[str]

    top_n: Optional[int] = 3  # 取前 N 个最相关的结果

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return AliyunBaiLianReranker(model=model_name,
                                     api_key=model_credential.get('dashscope_api_key'),
                                     top_n=model_kwargs.get('top_n', 3))

    def compress_documents(self, documents: Sequence[Document], query: str, callbacks: Optional[Callbacks] = None) -> \
            Sequence[Document]:
        if not documents:
            return []

        texts = [doc.page_content for doc in documents]
        resp = dashscope.TextReRank.call(
            model=self.model,
            query=query,
            documents=texts,
            top_n=self.top_n,
            api_key=self.api_key,
            return_documents=True
        )
        if resp.status_code == HTTPStatus.OK:
            return [
                Document(
                    page_content=item.get('document', {}).get('text', ''),
                    metadata={'relevance_score': item.get('relevance_score')}
                )
                for item in resp.output.get('results', [])
            ]
        else:
            return []
