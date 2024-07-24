from setting.models_provider.base_model_provider import MaxKBBaseModel
from typing import Dict
import requests


class TencentEmbeddingModel(MaxKBBaseModel):
    def __init__(self, secret_id: str, secret_key: str, api_base: str, model_name: str):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.api_base = api_base
        self.model_name = model_name

    @staticmethod
    def new_instance(model_type: str, model_name: str, model_credential: Dict[str, str], **model_kwargs):
        return TencentEmbeddingModel(
            secret_id=model_credential.get('SecretId'),
            secret_key=model_credential.get('SecretKey'),
            api_base=model_credential.get('api_base'),
            model_name=model_name,
        )


    def _generate_auth_token(self):
        # Example method to generate an authentication token for the model API
        return f"{self.secret_id}:{self.secret_key}"
