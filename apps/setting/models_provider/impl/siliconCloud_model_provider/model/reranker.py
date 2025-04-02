# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： siliconcloud_reranker.py
    @date：2024/9/10 9:45
    @desc: SiliconCloud 文档重排封装
"""

from typing import Sequence, Optional, Any, Dict
import requests

from langchain_core.callbacks import Callbacks
from langchain_core.documents import BaseDocumentCompressor, Document

from setting.models_provider.base_model_provider import MaxKBBaseModel
from django.utils.translation import gettext as _


class SiliconCloudReranker(MaxKBBaseModel, BaseDocumentCompressor):
    api_base: Optional[str]
    """SiliconCloud API URL"""
    model: Optional[str]
    """SiliconCloud 重排模型 ID"""
    api_key: Optional[str]
    """API Key"""

    top_n: Optional[int] = 3  # 取前 N 个最相关的结果

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return SiliconCloudReranker(
            api_base=model_credential.get('api_base'),
            model=model_name,
            api_key=model_credential.get('api_key'),
            top_n=model_kwargs.get('top_n', 3)
        )

    def compress_documents(self, documents: Sequence[Document], query: str, callbacks: Optional[Callbacks] = None) -> \
            Sequence[Document]:
        if not documents:
            return []

        # 预处理文本
        texts = [doc.page_content for doc in documents]

        # 发送请求到 SiliconCloud API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "query": query,
            "documents": texts,
            "top_n": self.top_n,
            "return_documents": True,
        }

        response = requests.post(f"{self.api_base}/rerank", json=payload, headers=headers)

        if response.status_code != 200:
            raise RuntimeError(f"SiliconCloud API 请求失败: {response.text}")

        res = response.json()

        # 解析返回结果
        return [
            Document(
                page_content=item.get('document', {}).get('text', ''),
                metadata={'relevance_score': item.get('relevance_score')}
            )
            for item in res.get('results', [])
        ]
