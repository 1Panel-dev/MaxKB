# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： embedding.py
    @date：2024/7/12 15:02
    @desc:
"""
from typing import Dict, List

from langchain_community.embeddings import OllamaEmbeddings

from setting.models_provider.base_model_provider import MaxKBBaseModel


class OllamaEmbedding(MaxKBBaseModel, OllamaEmbeddings):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return OllamaEmbedding(
            model=model_name,
            base_url=model_credential.get('api_base'),
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents using an Ollama deployed embedding model.

        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        instruction_pairs = [f"{text}" for text in texts]
        embeddings = self._embed(instruction_pairs)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a query using a Ollama deployed embedding model.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        instruction_pair = f"{text}"
        embedding = self._embed([instruction_pair])[0]
        return embedding
