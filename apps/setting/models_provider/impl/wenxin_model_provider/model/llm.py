# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： llm.py
    @date：2023/11/10 17:45
    @desc:
"""
import uuid
from typing import List, Dict, Optional, Any, Iterator

from langchain_community.chat_models.baidu_qianfan_endpoint import _convert_dict_to_message, QianfanChatEndpoint
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.outputs import ChatGenerationChunk
from setting.models_provider.base_model_provider import MaxKBBaseModel
from langchain_core.messages import (
    AIMessageChunk,
    BaseMessage,
)


class QianfanChatModel(MaxKBBaseModel, QianfanChatEndpoint):
    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {}
        if 'max_tokens' in model_kwargs and model_kwargs['max_tokens'] is not None:
            optional_params['max_output_tokens'] = model_kwargs['max_tokens']
        if 'temperature' in model_kwargs and model_kwargs['temperature'] is not None:
            optional_params['temperature'] = model_kwargs['temperature']
        return QianfanChatModel(model=model_name,
                                qianfan_ak=model_credential.get('api_key'),
                                qianfan_sk=model_credential.get('secret_key'),
                                streaming=model_kwargs.get('streaming', False),
                                init_kwargs=optional_params)

    usage_metadata: dict = {}

    def get_last_generation_info(self) -> Optional[Dict[str, Any]]:
        return self.usage_metadata

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        return self.usage_metadata.get('prompt_tokens', 0)

    def get_num_tokens(self, text: str) -> int:
        return self.usage_metadata.get('completion_tokens', 0)

    def _stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        kwargs = {**self.init_kwargs, **kwargs}
        params = self._convert_prompt_msg_params(messages, **kwargs)
        params["stop"] = stop
        params["stream"] = True
        for res in self.client.do(**params):
            if res:
                msg = _convert_dict_to_message(res)
                additional_kwargs = msg.additional_kwargs.get("function_call", {})
                if msg.content == "" or res.get("body").get("is_end"):
                    token_usage = res.get("body").get("usage")
                    self.usage_metadata = token_usage
                chunk = ChatGenerationChunk(
                    text=res["result"],
                    message=AIMessageChunk(  # type: ignore[call-arg]
                        content=msg.content,
                        role="assistant",
                        additional_kwargs=additional_kwargs,
                    ),
                    generation_info=msg.additional_kwargs,
                )
                if run_manager:
                    run_manager.on_llm_new_token(chunk.text, chunk=chunk)
                yield chunk
