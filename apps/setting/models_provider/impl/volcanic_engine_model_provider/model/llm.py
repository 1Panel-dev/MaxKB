from typing import List, Dict

from setting.models_provider.base_model_provider import MaxKBBaseModel

from setting.models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class VolcanicEngineChatModel(MaxKBBaseModel, BaseChatOpenAI):
    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return VolcanicEngineChatModel(
            model=model_name,
            openai_api_base=model_credential.get('api_base'),
            openai_api_key=model_credential.get('api_key'),
            extra_body=optional_params
        )
