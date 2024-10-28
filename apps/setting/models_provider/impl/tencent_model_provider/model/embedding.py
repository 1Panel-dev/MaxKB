 
from typing import Dict, List

from langchain_core.embeddings import Embeddings
from tencentcloud.common import credential
from tencentcloud.hunyuan.v20230901.hunyuan_client import HunyuanClient
from tencentcloud.hunyuan.v20230901.models import GetEmbeddingRequest

from setting.models_provider.base_model_provider import MaxKBBaseModel


class TencentEmbeddingModel(MaxKBBaseModel, Embeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        request = GetEmbeddingRequest()
        request.Input = text
        res = self.client.GetEmbedding(request)
        return res.Data[0].Embedding

    def __init__(self, secret_id: str, secret_key: str, model_name: str):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.model_name = model_name
        cred = credential.Credential(
            secret_id, secret_key
        )
        self.client = HunyuanClient(cred, "")

    @staticmethod
    def new_instance(model_type: str, model_name: str, model_credential: Dict[str, str], **model_kwargs):
        return TencentEmbeddingModel(
            secret_id=model_credential.get('SecretId'),
            secret_key=model_credential.get('SecretKey'),
            model_name=model_name,
        )

    def _generate_auth_token(self):
        # Example method to generate an authentication token for the model API
        return f"{self.secret_id}:{self.secret_key}"
