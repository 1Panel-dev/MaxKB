from typing import Dict, List

from langchain_core.messages import BaseMessage, get_buffer_string
from langchain_openai import AzureChatOpenAI

from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel


def custom_get_token_ids(text: str):
    tokenizer = TokenizerManage.get_tokenizer()
    return tokenizer.encode(text)


class AzureOpenAIImage(MaxKBBaseModel, AzureChatOpenAI):

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return AzureOpenAIImage(
            model_name=model_name,
            openai_api_key=model_credential.get('api_key'),
            azure_endpoint=model_credential.get('api_base'),
            openai_api_version=model_credential.get('api_version'),
            openai_api_type="azure",
            streaming=True,
            **optional_params,
        )

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        try:
            return super().get_num_tokens_from_messages(messages)
        except Exception as e:
            tokenizer = TokenizerManage.get_tokenizer()
            return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])

    def get_num_tokens(self, text: str) -> int:
        try:
            return super().get_num_tokens(text)
        except Exception as e:
            tokenizer = TokenizerManage.get_tokenizer()
            return len(tokenizer.encode(text))
