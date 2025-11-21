from typing import Dict

from langchain_google_genai import ChatGoogleGenerativeAI

from common.config.tokenizer_manage_config import TokenizerManage
from models_provider.base_model_provider import MaxKBBaseModel


def custom_get_token_ids(text: str):
    tokenizer = TokenizerManage.get_tokenizer()
    return tokenizer.encode(text)


class GeminiImage(MaxKBBaseModel, ChatGoogleGenerativeAI):

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return GeminiImage(
            model=model_name,
            google_api_key=model_credential.get('api_key'),
            **optional_params,
        )
