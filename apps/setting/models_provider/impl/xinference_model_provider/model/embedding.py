# coding=utf-8
import threading
from typing import Dict, Optional, List, Any

from langchain_core.embeddings import Embeddings

from setting.models_provider.base_model_provider import MaxKBBaseModel


class XinferenceEmbedding(MaxKBBaseModel, Embeddings):
    client: Any
    server_url: Optional[str]
    """URL of the xinference server"""
    model_uid: Optional[str]
    """UID of the launched model"""

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return XinferenceEmbedding(
            model_uid=model_name,
            server_url=model_credential.get('api_base'),
            api_key=model_credential.get('api_key'),
        )

    def down_model(self):
        self.client.launch_model(model_name=self.model_uid, model_type="embedding")

    def start_down_model_thread(self):
        thread = threading.Thread(target=self.down_model)
        thread.daemon = True
        thread.start()

    def __init__(
            self, server_url: Optional[str] = None, model_uid: Optional[str] = None,
            api_key: Optional[str] = None
    ):
        try:
            from xinference.client import RESTfulClient
        except ImportError:
            try:
                from xinference_client import RESTfulClient
            except ImportError as e:
                raise ImportError(
                    "Could not import RESTfulClient from xinference. Please install it"
                    " with `pip install xinference` or `pip install xinference_client`."
                ) from e

        if server_url is None:
            raise ValueError("Please provide server URL")

        if model_uid is None:
            raise ValueError("Please provide the model UID")

        self.server_url = server_url

        self.model_uid = model_uid

        self.api_key = api_key

        self.client = RESTfulClient(server_url, api_key)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents using Xinference.
        Args:
            texts: The list of texts to embed.
        Returns:
            List of embeddings, one for each text.
        """

        model = self.client.get_model(self.model_uid)

        embeddings = [
            model.create_embedding(text)["data"][0]["embedding"] for text in texts
        ]
        return [list(map(float, e)) for e in embeddings]

    def embed_query(self, text: str) -> List[float]:
        """Embed a query of documents using Xinference.
        Args:
            text: The text to embed.
        Returns:
            Embeddings for the text.
        """

        model = self.client.get_model(self.model_uid)

        embedding_res = model.create_embedding(text)

        embedding = embedding_res["data"][0]["embedding"]

        return list(map(float, embedding))
