# coding=utf-8

from typing import List, Dict, Optional, Any, Iterator, Type, cast
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage, AIMessageChunk, BaseMessageChunk
from langchain_core.outputs import ChatGenerationChunk, ChatGeneration
from langchain_core.runnables import RunnableConfig, ensure_config
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import _convert_delta_to_message_chunk


class BaseChatOpenAI(ChatOpenAI):
    usage_metadata: dict = {}

    def get_last_generation_info(self) -> Optional[Dict[str, Any]]:
        return self.usage_metadata

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        return self.usage_metadata.get('input_tokens', 0)

    def get_num_tokens(self, text: str) -> int:
        return self.get_last_generation_info().get('output_tokens', 0)

    def _stream(
            self, *args: Any, stream_usage: Optional[bool] = None, **kwargs: Any
    ) -> Iterator[ChatGenerationChunk]:
        kwargs["stream"] = True
        kwargs["stream_options"] = {"include_usage": True}
        for chunk in super()._stream(*args, stream_usage=stream_usage, **kwargs):
            if chunk.message.usage_metadata is not None:
                self.usage_metadata = chunk.message.usage_metadata
            yield chunk

    def invoke(
            self,
            input: LanguageModelInput,
            config: Optional[RunnableConfig] = None,
            *,
            stop: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> BaseMessage:
        config = ensure_config(config)
        chat_result = cast(
            ChatGeneration,
            self.generate_prompt(
                [self._convert_input(input)],
                stop=stop,
                callbacks=config.get("callbacks"),
                tags=config.get("tags"),
                metadata=config.get("metadata"),
                run_name=config.get("run_name"),
                run_id=config.pop("run_id", None),
                **kwargs,
            ).generations[0][0],
        ).message
        self.usage_metadata = chat_result.response_metadata['token_usage']
        return chat_result
