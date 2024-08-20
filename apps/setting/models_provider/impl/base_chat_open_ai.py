# coding=utf-8

from typing import List, Dict, Optional, Any, Iterator, Type
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.messages import BaseMessage, AIMessageChunk, BaseMessageChunk
from langchain_core.outputs import ChatGenerationChunk
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import _convert_delta_to_message_chunk


class BaseChatOpenAI(ChatOpenAI):

    def get_last_generation_info(self) -> Optional[Dict[str, Any]]:
        return self.__dict__.get('_last_generation_info')

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        return self.get_last_generation_info().get('prompt_tokens', 0)

    def get_num_tokens(self, text: str) -> int:
        return self.get_last_generation_info().get('completion_tokens', 0)

    def _stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        kwargs["stream"] = True
        kwargs["stream_options"] = {"include_usage": True}
        payload = self._get_request_payload(messages, stop=stop, **kwargs)
        default_chunk_class: Type[BaseMessageChunk] = AIMessageChunk
        if self.include_response_headers:
            raw_response = self.client.with_raw_response.create(**payload)
            response = raw_response.parse()
            base_generation_info = {"headers": dict(raw_response.headers)}
        else:
            response = self.client.create(**payload)
            base_generation_info = {}
        with response:
            is_first_chunk = True
            for chunk in response:
                if not isinstance(chunk, dict):
                    chunk = chunk.model_dump()
                if (len(chunk["choices"]) == 0 or chunk["choices"][0]["finish_reason"] == "length" or
                    chunk["choices"][0]["finish_reason"] == "stop") and chunk.get("usage") is not None:
                    if token_usage := chunk.get("usage"):
                        self.__dict__.setdefault('_last_generation_info', {}).update(token_usage)
                        logprobs = None
                        continue
                else:
                    choice = chunk["choices"][0]
                    if choice["delta"] is None:
                        continue
                    message_chunk = _convert_delta_to_message_chunk(
                        choice["delta"], default_chunk_class
                    )
                    generation_info = {**base_generation_info} if is_first_chunk else {}
                    if finish_reason := choice.get("finish_reason"):
                        generation_info["finish_reason"] = finish_reason
                        if model_name := chunk.get("model"):
                            generation_info["model_name"] = model_name
                        if system_fingerprint := chunk.get("system_fingerprint"):
                            generation_info["system_fingerprint"] = system_fingerprint

                    logprobs = choice.get("logprobs")
                    if logprobs:
                        generation_info["logprobs"] = logprobs
                    default_chunk_class = message_chunk.__class__
                    generation_chunk = ChatGenerationChunk(
                        message=message_chunk, generation_info=generation_info or None
                    )
                if run_manager:
                    run_manager.on_llm_new_token(
                        generation_chunk.text, chunk=generation_chunk, logprobs=logprobs
                    )
                is_first_chunk = False
                yield generation_chunk
