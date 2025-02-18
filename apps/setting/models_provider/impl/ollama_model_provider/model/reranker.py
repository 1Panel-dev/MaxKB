from typing import Sequence, Optional, Any, Dict
from langchain_core.callbacks import Callbacks
from langchain_core.documents import BaseDocumentCompressor, Document
import requests

from setting.models_provider.base_model_provider import MaxKBBaseModel


class OllamaReranker(MaxKBBaseModel, BaseDocumentCompressor):
    api_base: Optional[str]
    """URL of the Ollama server"""
    model_name: Optional[str]
    """The model name to use for reranking"""
    api_key: Optional[str]

    @staticmethod
    def new_instance(model_name, model_credential: Dict[str, object], **model_kwargs):
        return OllamaReranker(api_base=model_credential.get('api_base'), model_name=model_name,
                              api_key=model_credential.get('api_key'), top_n=model_kwargs.get('top_n', 3))

    top_n: Optional[int] = 3

    def __init__(
            self, api_base: Optional[str] = None, model_name: Optional[str] = None, top_n=3,
            api_key: Optional[str] = None
    ):
        super().__init__()

        if api_base is None:
            raise ValueError("Please provide server URL")

        if model_name is None:
            raise ValueError("Please provide the model name")

        self.api_base = api_base
        self.model_name = model_name
        self.api_key = api_key
        self.top_n = top_n

    def compress_documents(self, documents: Sequence[Document], query: str, callbacks: Optional[Callbacks] = None) -> \
            Sequence[Document]:
        """
        Given a query and a set of documents, rerank them using Ollama API.
        """
        if not documents or len(documents) == 0:
            return []

        # Prepare the data to send to Ollama API
        headers = {
            'Authorization': f'Bearer {self.api_key}'  # Use API key for authentication if required
        }

        # Format the documents to be sent in a format understood by Ollama's API
        documents_text = [document.page_content for document in documents]

        # Make a POST request to Ollama's rerank API endpoint
        payload = {
            'model': self.model_name,  # Specify the model
            'query': query,
            'documents': documents_text,
            'top_n': self.top_n
        }

        try:
            response = requests.post(f'{self.api_base}/v1/rerank', headers=headers, json=payload)
            response.raise_for_status()
            res = response.json()

            # Ensure the response contains expected results
            if 'results' not in res:
                raise ValueError("The API response did not contain rerank results.")

            # Convert the API response into a list of Document objects with relevance scores
            ranked_documents = [
                Document(page_content=d['text'], metadata={'relevance_score': d['relevance_score']})
                for d in res['results']
            ]
            return ranked_documents

        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")
            return []  # Return an empty list if the request failed
