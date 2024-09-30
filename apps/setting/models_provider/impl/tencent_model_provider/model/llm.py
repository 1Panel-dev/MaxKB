# coding=utf-8

from typing import List, Dict, Optional, Any

from langchain_core.messages import BaseMessage, get_buffer_string
from common.config.tokenizer_manage_config import TokenizerManage
from setting.models_provider.base_model_provider import MaxKBBaseModel
from setting.models_provider.impl.tencent_model_provider.model.hunyuan import ChatHunyuan


class TencentModel(MaxKBBaseModel, ChatHunyuan):
    @staticmethod
    def is_cache_model():
        return False

    def __init__(self, model_name: str, credentials: Dict[str, str], streaming: bool = False, **kwargs):
        hunyuan_app_id = credentials.get('hunyuan_app_id')
        hunyuan_secret_id = credentials.get('hunyuan_secret_id')
        hunyuan_secret_key = credentials.get('hunyuan_secret_key')

        optional_params = {}
        if 'temperature' in kwargs:
            optional_params['temperature'] = kwargs['temperature']

        if not all([hunyuan_app_id, hunyuan_secret_id, hunyuan_secret_key]):
            raise ValueError(
                "All of 'hunyuan_app_id', 'hunyuan_secret_id', and 'hunyuan_secret_key' must be provided in credentials.")

        super().__init__(model=model_name, hunyuan_app_id=hunyuan_app_id, hunyuan_secret_id=hunyuan_secret_id,
                         hunyuan_secret_key=hunyuan_secret_key, streaming=streaming,
                         temperature=optional_params.get('temperature', 1.0)
                         )

    @staticmethod
    def new_instance(model_type: str, model_name: str, model_credential: Dict[str, object],
                     **model_kwargs) -> 'TencentModel':
        streaming = model_kwargs.pop('streaming', False)
        return TencentModel(model_name=model_name, credentials=model_credential, streaming=streaming, **model_kwargs)

    def get_last_generation_info(self) -> Optional[Dict[str, Any]]:
        return self.usage_metadata

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        return self.usage_metadata.get('PromptTokens', 0)

    def get_num_tokens(self, text: str) -> int:
        return self.usage_metadata.get('CompletionTokens', 0)
