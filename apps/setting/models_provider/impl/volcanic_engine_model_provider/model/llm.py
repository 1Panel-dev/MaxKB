from typing import List, Dict

from langchain_community.chat_models import VolcEngineMaasChat
from langchain_core.messages import BaseMessage, get_buffer_string

from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel
from langchain_openai import ChatOpenAI


class VolcanicEngineChatModel(MaxKBBaseModel, ChatOpenAI):
    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        volcanic_engine_chat = VolcanicEngineChatModel(
            model=model_name,
            volc_engine_maas_ak=model_credential.get("access_key_id"),
            volc_engine_maas_sk=model_credential.get("secret_access_key"),
        )
        return volcanic_engine_chat

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        tokenizer = TokenizerManage.get_tokenizer()
        return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])

    def get_num_tokens(self, text: str) -> int:
        tokenizer = TokenizerManage.get_tokenizer()
        return len(tokenizer.encode(text))
