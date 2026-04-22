from typing import Dict, List

from models_provider.base_model_provider import MaxKBBaseModel
from volcenginesdkarkruntime import Ark


class VolcanicEngineEmbeddingModel(MaxKBBaseModel):
    api_key: str
    model_name: str
    api_base: str
    params: Dict[str, object]

    def __init__(self, api_key: str, model: str, api_base: str, **params):
        self.client = Ark(
            api_key=api_key,
            base_url=api_base
        )
        self.model_name = model
        self.params = params

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return VolcanicEngineEmbeddingModel(
            api_key=model_credential.get("api_key"),
            model=model_name,
            api_base=model_credential.get("api_base"),
            **optional_params
        )

    def embed_query(self, text: str):
        res = self.embed_documents([text])
        return res[0]

    def embed_documents(
            self, texts: List[str]
    ) -> List[List[float]]:
        if self.model_name.startswith("doubao-embedding-vision-"):
            embeddings = []
            for text in texts:
                multimodal_input = {"type": "text", "text": text}
                resp = self.client.multimodal_embeddings.create(
                    model=self.model_name,
                    input=[multimodal_input],
                    encoding_format="float",
                    **(self.params or {})
                )
                embedding = self._extract_embedding(resp.data)
                if embedding is not None:
                    embeddings.append(embedding)
            return embeddings
        else:
            resp = self.client.embeddings.create(
                model=self.model_name,
                input=texts,
                **(self.params or {})
            )
            return [e.embedding for e in resp.data]

    def _extract_embedding(self, data):
        if isinstance(data, list) and len(data) > 0:
            item = data[0]
        else:
            item = data

        if hasattr(item, 'embedding'):
            return item.embedding
        elif isinstance(item, dict):
            return item.get('embedding')
        elif isinstance(item, list):
            return item
        return None
