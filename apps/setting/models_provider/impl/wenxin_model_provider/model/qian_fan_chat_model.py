# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： qian_fan_chat_model.py
    @date：2023/11/10 17:45
    @desc:
"""
from typing import Optional, List, Any, Iterator, cast

from langchain.callbacks.manager import CallbackManager
from langchain.chat_models.base import BaseChatModel
from langchain.load import dumpd
from langchain.schema import LLMResult
from langchain.schema.language_model import LanguageModelInput
from langchain.schema.messages import BaseMessageChunk, BaseMessage, HumanMessage, AIMessage, get_buffer_string
from langchain.schema.output import ChatGenerationChunk
from langchain.schema.runnable import RunnableConfig
from langchain_community.chat_models import QianfanChatEndpoint

from common.config.tokenizer_manage_config import TokenizerManage


class QianfanChatModel(QianfanChatEndpoint):

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        tokenizer = TokenizerManage.get_tokenizer()
        return sum([len(tokenizer.encode(get_buffer_string([m]))) for m in messages])

    def get_num_tokens(self, text: str) -> int:
        tokenizer = TokenizerManage.get_tokenizer()
        return len(tokenizer.encode(text))

    def stream(
            self,
            input: LanguageModelInput,
            config: Optional[RunnableConfig] = None,
            *,
            stop: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> Iterator[BaseMessageChunk]:
        if len(input) % 2 == 0:
            input = [HumanMessage(content='padding'), *input]
        input = [
            HumanMessage(content=input[index].content) if index % 2 == 0 else AIMessage(content=input[index].content)
            for index in range(0, len(input))]
        if type(self)._stream == BaseChatModel._stream:
            # model doesn't implement streaming, so use default implementation
            yield cast(
                BaseMessageChunk, self.invoke(input, config=config, stop=stop, **kwargs)
            )
        else:
            config = config or {}
            messages = self._convert_input(input).to_messages()
            params = self._get_invocation_params(stop=stop, **kwargs)
            options = {"stop": stop, **kwargs}
            callback_manager = CallbackManager.configure(
                config.get("callbacks"),
                self.callbacks,
                self.verbose,
                config.get("tags"),
                self.tags,
                config.get("metadata"),
                self.metadata,
            )
            (run_manager,) = callback_manager.on_chat_model_start(
                dumpd(self),
                [messages],
                invocation_params=params,
                options=options,
                name=config.get("run_name"),
            )
            try:
                generation: Optional[ChatGenerationChunk] = None
                for chunk in self._stream(
                        messages, stop=stop, run_manager=run_manager, **kwargs
                ):
                    yield chunk.message
                    if generation is None:
                        generation = chunk
                assert generation is not None
            except BaseException as e:
                run_manager.on_llm_error(e)
                raise e
            else:
                run_manager.on_llm_end(
                    LLMResult(generations=[[generation]]),
                )
