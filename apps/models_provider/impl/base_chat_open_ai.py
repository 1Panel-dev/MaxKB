# coding=utf-8
import warnings
from typing import List, Dict, Optional, Any, Iterator, cast, Type, Union

import openai
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage, get_buffer_string, BaseMessageChunk, AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk, ChatGeneration
from langchain_core.runnables import RunnableConfig, ensure_config
from langchain_core.utils.pydantic import is_basemodel_subclass
from langchain_openai import ChatOpenAI

from common.config.tokenizer_manage_config import TokenizerManage


def custom_get_token_ids(text: str):
    tokenizer = TokenizerManage.get_tokenizer()
    return tokenizer.encode(text)


class BaseChatOpenAI(ChatOpenAI):
    usage_metadata: dict = {}
    custom_get_token_ids = custom_get_token_ids

    def get_last_generation_info(self) -> Optional[Dict[str, Any]]:
        return self.usage_metadata

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
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

    def _stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        kwargs["stream"] = True
        kwargs["stream_options"] = {"include_usage": True}
        """Set default stream_options."""
        stream_usage = self._should_stream_usage(kwargs.get('stream_usage'), **kwargs)
        # Note: stream_options is not a valid parameter for Azure OpenAI.
        # To support users proxying Azure through ChatOpenAI, here we only specify
        # stream_options if include_usage is set to True.
        # See https://learn.microsoft.com/en-us/azure/ai-services/openai/whats-new
        # for release notes.
        if stream_usage:
            kwargs["stream_options"] = {"include_usage": stream_usage}

        payload = self._get_request_payload(messages, stop=stop, **kwargs)
        default_chunk_class: Type[BaseMessageChunk] = AIMessageChunk
        base_generation_info = {}

        if "response_format" in payload and is_basemodel_subclass(
                payload["response_format"]
        ):
            # TODO: Add support for streaming with Pydantic response_format.
            warnings.warn("Streaming with Pydantic response_format not yet supported.")
            chat_result = self._generate(
                messages, stop, run_manager=run_manager, **kwargs
            )
            msg = chat_result.generations[0].message
            yield ChatGenerationChunk(
                message=AIMessageChunk(
                    **msg.dict(exclude={"type", "additional_kwargs"}),
                    # preserve the "parsed" Pydantic object without converting to dict
                    additional_kwargs=msg.additional_kwargs,
                ),
                generation_info=chat_result.generations[0].generation_info,
            )
            return
        if self.include_response_headers:
            raw_response = self.client.with_raw_response.create(**payload)
            response = raw_response.parse()
            base_generation_info = {"headers": dict(raw_response.headers)}
        else:
            response = self.client.create(**payload)
        with response:
            is_first_chunk = True
            for chunk in response:
                if not isinstance(chunk, dict):
                    chunk = chunk.model_dump()

                generation_chunk = super()._convert_chunk_to_generation_chunk(
                    chunk,
                    default_chunk_class,
                    base_generation_info if is_first_chunk else {},
                )
                if generation_chunk is None:
                    continue

                # custom code
                if len(chunk['choices']) > 0 and 'reasoning_content' in chunk['choices'][0]['delta']:
                    generation_chunk.message.additional_kwargs["reasoning_content"] = chunk['choices'][0]['delta'][
                        'reasoning_content']

                default_chunk_class = generation_chunk.message.__class__
                logprobs = (generation_chunk.generation_info or {}).get("logprobs")
                if run_manager:
                    run_manager.on_llm_new_token(
                        generation_chunk.text, chunk=generation_chunk, logprobs=logprobs
                    )
                is_first_chunk = False
                # custom code
                if generation_chunk.message.usage_metadata is not None:
                    self.usage_metadata = generation_chunk.message.usage_metadata
                yield generation_chunk

    def _create_chat_result(self,
                            response: Union[dict, openai.BaseModel],
                            generation_info: Optional[Dict] = None):
        result = super()._create_chat_result(response, generation_info)
        try:
            reasoning_content = ''
            reasoning_content_enable = False
            for res in response.choices:
                if 'reasoning_content' in res.message.model_extra:
                    reasoning_content_enable = True
                    _reasoning_content = res.message.model_extra.get('reasoning_content')
                    if _reasoning_content is not None:
                        reasoning_content += _reasoning_content
            if reasoning_content_enable:
                result.llm_output['reasoning_content'] = reasoning_content
        except Exception as e:
            pass
        return result

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
        self.usage_metadata = chat_result.response_metadata[
            'token_usage'] if 'token_usage' in chat_result.response_metadata else chat_result.usage_metadata
        return chat_result
