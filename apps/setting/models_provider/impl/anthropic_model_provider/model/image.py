from typing import Dict

from langchain_anthropic import ChatAnthropic

from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel


def custom_get_token_ids(text: str):
    tokenizer = TokenizerManage.get_tokenizer()
    return tokenizer.encode(text)


class AnthropicImage(MaxKBBaseModel, ChatAnthropic):

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return AnthropicImage(
            model=model_name,
            anthropic_api_url=model_credential.get('api_base'),
            anthropic_api_key=model_credential.get('api_key'),
            # stream_options={"include_usage": True},
            streaming=True,
            **optional_params,
        )
