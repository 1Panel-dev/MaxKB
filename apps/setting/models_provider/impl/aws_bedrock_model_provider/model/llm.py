from typing import List, Dict, Any
from langchain_community.chat_models import BedrockChat
from langchain_core.messages import BaseMessage, get_buffer_string
from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel


class BedrockModel(MaxKBBaseModel, BedrockChat):

    def __init__(self, model_id: str, region_name: str, credentials_profile_name: str,
                 streaming: bool = False, **kwargs):
        super().__init__(model_id=model_id, region_name=region_name,
                         credentials_profile_name=credentials_profile_name, streaming=streaming, **kwargs)

    @classmethod
    def new_instance(cls, model_type: str, model_name: str, model_credential: Dict[str, str],
                     **model_kwargs) -> 'BedrockModel':
        return cls(
            model_id=model_name,
            region_name=model_credential['region_name'],
            credentials_profile_name=model_credential['credentials_profile_name'],
            streaming=model_kwargs.pop('streaming', False),
            **model_kwargs
        )

    def _get_num_tokens(self, content: str) -> int:
        """Helper method to count tokens in a string."""
        tokenizer = TokenizerManage.get_tokenizer()
        return len(tokenizer.encode(content))

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        return sum(self._get_num_tokens(get_buffer_string([message])) for message in messages)

    def get_num_tokens(self, text: str) -> int:
        return self._get_num_tokens(text)
