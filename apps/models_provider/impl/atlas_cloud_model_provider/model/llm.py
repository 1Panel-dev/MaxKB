from typing import Dict

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.atlas_cloud_model_provider.constants import ATLAS_CLOUD_API_BASE
from models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class AtlasCloudChatModel(MaxKBBaseModel, BaseChatOpenAI):
    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return AtlasCloudChatModel(
            model=model_name,
            openai_api_base=model_credential.get("api_base") or ATLAS_CLOUD_API_BASE,
            openai_api_key=model_credential.get("api_key"),
            **optional_params,
        )
