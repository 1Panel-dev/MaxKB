from langchain_community.embeddings import BedrockEmbeddings

from setting.models_provider.base_model_provider import MaxKBBaseModel
from typing import Dict, List


class BedrockEmbeddingModel(MaxKBBaseModel, BedrockEmbeddings):
    def __init__(self, model_id: str, region_name: str, credentials_profile_name: str,
                 **kwargs):
        super().__init__(model_id=model_id, region_name=region_name,
                         credentials_profile_name=credentials_profile_name, **kwargs)

    @classmethod
    def new_instance(cls, model_type: str, model_name: str, model_credential: Dict[str, str],
                     **model_kwargs) -> 'BedrockModel':
        return cls(
            model_id=model_name,
            region_name=model_credential['region_name'],
            credentials_profile_name=model_credential['credentials_profile_name'],
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Compute doc embeddings using a Bedrock model.

        Args:
            texts: The list of texts to embed

        Returns:
            List of embeddings, one for each text.
        """
        results = []
        for text in texts:
            response = self._embedding_func(text)

            if self.normalize:
                response = self._normalize_vector(response)

            results.append(response)

        return results

    def embed_query(self, text: str) -> List[float]:
        """Compute query embeddings using a Bedrock model.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        embedding = self._embedding_func(text)

        if self.normalize:
            return self._normalize_vector(embedding)

        return embedding
