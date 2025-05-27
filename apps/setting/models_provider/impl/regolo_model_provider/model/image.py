from typing import Dict

from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class RegoloImage(MaxKBBaseModel, BaseChatOpenAI):

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return RegoloImage(
            model_name=model_name,
            openai_api_base="https://api.regolo.ai/v1",
            openai_api_key=model_credential.get('api_key'),
            streaming=True,
            stream_usage=True,
            extra_body=optional_params
        )
