from typing import Dict

from langchain_community.embeddings import VolcanoEmbeddings

from setting.models_provider.base_model_provider import MaxKBBaseModel


class VolcanicEngineEmbeddingModel(MaxKBBaseModel, VolcanoEmbeddings):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        return VolcanicEngineEmbeddingModel(
            api_key=model_credential.get('api_key'),
            model=model_name,
            openai_api_base=model_credential.get('api_base'),
        )
