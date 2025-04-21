from typing import Dict, List

from langchain_core.messages import get_buffer_string, BaseMessage

from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class VllmImage(MaxKBBaseModel, BaseChatOpenAI):

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return VllmImage(
            model_name=model_name,
            openai_api_base=model_credential.get('api_base'),
            openai_api_key=model_credential.get('api_key'),
            # stream_options={"include_usage": True},
            streaming=True,
            stream_usage=True,
            extra_body=optional_params
        )

    def is_cache_model(self):
        return False

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        if self.usage_metadata is None or self.usage_metadata == {}:
            tokenizer = TokenizerManage.get_tokenizer()
            return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])
        return self.usage_metadata.get('input_tokens', 0)

    def get_num_tokens(self, text: str) -> int:
        if self.usage_metadata is None or self.usage_metadata == {}:
            tokenizer = TokenizerManage.get_tokenizer()
            return len(tokenizer.encode(text))
        return self.get_last_generation_info().get('output_tokens', 0)
