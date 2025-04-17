from typing import Dict

from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class SiliconCloudImage(MaxKBBaseModel, BaseChatOpenAI):

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return SiliconCloudImage(
            model_name=model_name,
            openai_api_base=model_credential.get('api_base'),
            openai_api_key=model_credential.get('api_key'),
            # stream_options={"include_usage": True},
            streaming=True,
            stream_usage=True,
            **optional_params,
        )
