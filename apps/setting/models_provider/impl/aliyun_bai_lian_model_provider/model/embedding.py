# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/10/16 16:34
    @desc:
"""
from functools import reduce
from typing import Dict, List

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.embeddings.dashscope import embed_with_retry

from setting.models_provider.base_model_provider import MaxKBBaseModel


def proxy_embed_documents(texts: List[str], step_size, embed_documents):
    value = [embed_documents(texts[start_index:start_index + step_size]) for start_index in
             range(0, len(texts), step_size)]
    return reduce(lambda x, y: [*x, *y], value, [])


class AliyunBaiLianEmbedding(MaxKBBaseModel, DashScopeEmbeddings):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return AliyunBaiLianEmbedding(
            model=model_name,
            dashscope_api_key=model_credential.get('dashscope_api_key')
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self.model == 'text-embedding-v3':
            return proxy_embed_documents(texts, 6, self._embed_documents)
        return self._embed_documents(texts)

    def _embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Call out to DashScope's embedding endpoint for embedding search docs.

        Args:
            texts: The list of texts to embed.
            chunk_size: The chunk size of embeddings. If None, will use the chunk size
                specified by the class.

        Returns:
            List of embeddings, one for each text.
        """
        embeddings = embed_with_retry(
            self, input=texts, text_type="document", model=self.model
        )
        embedding_list = [item["embedding"] for item in embeddings]
        return embedding_list

    def embed_query(self, text: str) -> List[float]:
        """Call out to DashScope's embedding endpoint for embedding query text.

        Args:
            text: The text to embed.

        Returns:
            Embedding for the text.
        """
        embedding = embed_with_retry(
            self, input=[text], text_type="document", model=self.model
        )[0]["embedding"]
        return embedding
