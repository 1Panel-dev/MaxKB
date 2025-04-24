# coding=utf-8
from typing import Dict, Optional, Any, Iterator, cast, Union, Sequence, Callable, Mapping

from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage, get_buffer_string, BaseMessageChunk, HumanMessageChunk, AIMessageChunk, \
    SystemMessageChunk, FunctionMessageChunk, ChatMessageChunk
from langchain_core.messages.ai import UsageMetadata
from langchain_core.messages.tool import tool_call_chunk, ToolMessageChunk
from langchain_core.outputs import ChatGenerationChunk
from langchain_core.runnables import RunnableConfig, ensure_config
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import _create_usage_metadata

from common.config.tokenizer_manage_config import TokenizerManage


def custom_get_token_ids(text: str):
    tokenizer = TokenizerManage.get_tokenizer()
    return tokenizer.encode(text)


def _convert_delta_to_message_chunk(
        _dict: Mapping[str, Any], default_class: type[BaseMessageChunk]
) -> BaseMessageChunk:
    id_ = _dict.get("id")
    role = cast(str, _dict.get("role"))
    content = cast(str, _dict.get("content") or "")
    additional_kwargs: dict = {}
    if 'reasoning_content' in _dict:
        additional_kwargs['reasoning_content'] = _dict.get('reasoning_content')
    if _dict.get("function_call"):
        function_call = dict(_dict["function_call"])
        if "name" in function_call and function_call["name"] is None:
            function_call["name"] = ""
        additional_kwargs["function_call"] = function_call
    tool_call_chunks = []
    if raw_tool_calls := _dict.get("tool_calls"):
        additional_kwargs["tool_calls"] = raw_tool_calls
        try:
            tool_call_chunks = [
                tool_call_chunk(
                    name=rtc["function"].get("name"),
                    args=rtc["function"].get("arguments"),
                    id=rtc.get("id"),
                    index=rtc["index"],
                )
                for rtc in raw_tool_calls
            ]
        except KeyError:
            pass

    if role == "user" or default_class == HumanMessageChunk:
        return HumanMessageChunk(content=content, id=id_)
    elif role == "assistant" or default_class == AIMessageChunk:
        return AIMessageChunk(
            content=content,
            additional_kwargs=additional_kwargs,
            id=id_,
            tool_call_chunks=tool_call_chunks,  # type: ignore[arg-type]
        )
    elif role in ("system", "developer") or default_class == SystemMessageChunk:
        if role == "developer":
            additional_kwargs = {"__openai_role__": "developer"}
        else:
            additional_kwargs = {}
        return SystemMessageChunk(
            content=content, id=id_, additional_kwargs=additional_kwargs
        )
    elif role == "function" or default_class == FunctionMessageChunk:
        return FunctionMessageChunk(content=content, name=_dict["name"], id=id_)
    elif role == "tool" or default_class == ToolMessageChunk:
        return ToolMessageChunk(
            content=content, tool_call_id=_dict["tool_call_id"], id=id_
        )
    elif role or default_class == ChatMessageChunk:
        return ChatMessageChunk(content=content, role=role, id=id_)
    else:
        return default_class(content=content, id=id_)  # type: ignore


class BaseChatOpenAI(ChatOpenAI):
    usage_metadata: dict = {}
    custom_get_token_ids = custom_get_token_ids

    def get_last_generation_info(self) -> Optional[Dict[str, Any]]:
        return self.usage_metadata

    def get_num_tokens_from_messages(
            self,
            messages: list[BaseMessage],
            tools: Optional[
                Sequence[Union[dict[str, Any], type, Callable, BaseTool]]
            ] = None,
    ) -> int:
        if self.usage_metadata is None or self.usage_metadata == {}:
            try:
                return super().get_num_tokens_from_messages(messages)
            except Exception as e:
                tokenizer = TokenizerManage.get_tokenizer()
                return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])
        return self.usage_metadata.get('input_tokens', 0)

    def get_num_tokens(self, text: str) -> int:
        if self.usage_metadata is None or self.usage_metadata == {}:
            try:
                return super().get_num_tokens(text)
            except Exception as e:
                tokenizer = TokenizerManage.get_tokenizer()
                return len(tokenizer.encode(text))
        return self.get_last_generation_info().get('output_tokens', 0)

    def _stream(self, *args: Any, **kwargs: Any) -> Iterator[ChatGenerationChunk]:
        kwargs['stream_usage'] = True
        for chunk in super()._stream(*args, **kwargs):
            if chunk.message.usage_metadata is not None:
                self.usage_metadata = chunk.message.usage_metadata
            yield chunk

    def _convert_chunk_to_generation_chunk(
            self,
            chunk: dict,
            default_chunk_class: type,
            base_generation_info: Optional[dict],
    ) -> Optional[ChatGenerationChunk]:
        if chunk.get("type") == "content.delta":  # from beta.chat.completions.stream
            return None
        token_usage = chunk.get("usage")
        choices = (
                chunk.get("choices", [])
                # from beta.chat.completions.stream
                or chunk.get("chunk", {}).get("choices", [])
        )

        usage_metadata: Optional[UsageMetadata] = (
            _create_usage_metadata(token_usage) if token_usage else None
        )
        if len(choices) == 0:
            # logprobs is implicitly None
            generation_chunk = ChatGenerationChunk(
                message=default_chunk_class(content="", usage_metadata=usage_metadata)
            )
            return generation_chunk

        choice = choices[0]
        if choice["delta"] is None:
            return None

        message_chunk = _convert_delta_to_message_chunk(
            choice["delta"], default_chunk_class
        )
        generation_info = {**base_generation_info} if base_generation_info else {}

        if finish_reason := choice.get("finish_reason"):
            generation_info["finish_reason"] = finish_reason
            if model_name := chunk.get("model"):
                generation_info["model_name"] = model_name
            if system_fingerprint := chunk.get("system_fingerprint"):
                generation_info["system_fingerprint"] = system_fingerprint

        logprobs = choice.get("logprobs")
        if logprobs:
            generation_info["logprobs"] = logprobs

        if usage_metadata and isinstance(message_chunk, AIMessageChunk):
            message_chunk.usage_metadata = usage_metadata

        generation_chunk = ChatGenerationChunk(
            message=message_chunk, generation_info=generation_info or None
        )
        return generation_chunk

    def invoke(
            self,
            input: LanguageModelInput,
            config: Optional[RunnableConfig] = None,
            *,
            stop: Optional[list[str]] = None,
            **kwargs: Any,
    ) -> BaseMessage:
        config = ensure_config(config)
        chat_result = cast(
            "ChatGeneration",
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

        self.usage_metadata = chat_result.response_metadata[
            'token_usage'] if 'token_usage' in chat_result.response_metadata else chat_result.usage_metadata
        return chat_result
