import json
import uuid
from typing import Any, Dict, Iterator, List, Mapping, Optional, Union

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    ChatMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.messages.ai import UsageMetadata
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.utils import convert_to_secret_str, get_from_dict_or_env
from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator


def convert_message_to_dict(message: BaseMessage) -> dict:
    message_dict: Dict[str, Any]
    if isinstance(message, ChatMessage):
        message_dict = {"role": message.role, "content": message.content}
    elif isinstance(message, HumanMessage):
        message_dict = {"role": "user", "content": message.content}
    elif isinstance(message, AIMessage):
        message_dict = {"role": "assistant", "content": message.content}
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            message_dict["function_call"] = {
                "name": tool_call["name"],
                "arguments": json.dumps(tool_call["args"], ensure_ascii=False),
            }
            message_dict["content"] = None
    elif isinstance(message, (FunctionMessage, ToolMessage)):
        message_dict = {
            "role": "function",
            "content": _create_tool_content(message.content),
            "name": message.name or message.additional_kwargs.get("name"),
        }
    else:
        raise TypeError(f"Got unknown type {message}")
    return message_dict


def _create_tool_content(content: Union[str, List[Union[str, Dict[Any, Any]]]]) -> str:
    if isinstance(content, str):
        try:
            if isinstance(json.loads(content), dict):
                return content
        except json.JSONDecodeError:
            pass
    return json.dumps({"tool_result": content}, ensure_ascii=False)


def _convert_dict_to_message(_dict: Mapping[str, Any]) -> AIMessage:
    content = _dict.get("result", "") or ""
    additional_kwargs: Mapping[str, Any] = {}
    if _dict.get("function_call"):
        additional_kwargs = {"function_call": dict(_dict["function_call"])}
        if "thoughts" in additional_kwargs["function_call"]:
            additional_kwargs["function_call"].pop("thoughts")

    additional_kwargs = {**_dict.get("body", {}), **additional_kwargs}
    msg_additional_kwargs = {
        "finish_reason": additional_kwargs.get("finish_reason", ""),
        "request_id": additional_kwargs.get("id", ""),
        "object": additional_kwargs.get("object", ""),
        "search_info": additional_kwargs.get("search_info", []),
    }

    if additional_kwargs.get("function_call", {}):
        function_call = additional_kwargs.get("function_call", {})
        msg_additional_kwargs["function_call"] = function_call
        msg_additional_kwargs["tool_calls"] = [
            {
                "type": "function",
                "function": function_call,
                "id": str(uuid.uuid4()),
            }
        ]

    message = AIMessage(content=content, additional_kwargs=msg_additional_kwargs)
    if usage := additional_kwargs.get("usage"):
        message.usage_metadata = UsageMetadata(
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
        )
    return message


class QianfanChatEndpoint(BaseChatModel):
    init_kwargs: Dict[str, Any] = Field(default_factory=dict)
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    client: Any = None
    qianfan_ak: Optional[SecretStr] = Field(default=None, alias="api_key")
    qianfan_sk: Optional[SecretStr] = Field(default=None, alias="secret_key")
    streaming: bool = False
    request_timeout: int = Field(60, alias="timeout")
    top_p: float = 0.8
    temperature: float = 0.95
    penalty_score: float = 1
    model: Optional[str] = Field(default=None)
    endpoint: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["qianfan_ak"] = convert_to_secret_str(
            get_from_dict_or_env(values, ["qianfan_ak", "api_key"], "QIANFAN_AK", default="")
        )
        values["qianfan_sk"] = convert_to_secret_str(
            get_from_dict_or_env(values, ["qianfan_sk", "secret_key"], "QIANFAN_SK", default="")
        )

        default_values = {
            "model": values.get("model"),
            "streaming": values.get("streaming", False),
            **values.get("init_kwargs", {}),
        }
        if values["qianfan_ak"].get_secret_value():
            default_values["ak"] = values["qianfan_ak"].get_secret_value()
        if values["qianfan_sk"].get_secret_value():
            default_values["sk"] = values["qianfan_sk"].get_secret_value()
        if values.get("endpoint"):
            default_values["endpoint"] = values["endpoint"]

        import qianfan

        values["client"] = qianfan.ChatCompletion(**default_values)
        return values

    @property
    def _llm_type(self) -> str:
        return "baidu-qianfan-chat"

    @property
    def _default_params(self) -> Dict[str, Any]:
        normal_params = {
            "model": self.model,
            "endpoint": self.endpoint,
            "stream": self.streaming,
            "request_timeout": self.request_timeout,
            "top_p": self.top_p,
            "temperature": self.temperature,
            "penalty_score": self.penalty_score,
        }
        return {**normal_params, **self.model_kwargs}

    def _convert_prompt_msg_params(self, messages: List[BaseMessage], **kwargs: Any) -> Dict[str, Any]:
        message_params: Dict[str, Any] = {
            "messages": [convert_message_to_dict(message) for message in messages if not isinstance(message, SystemMessage)]
        }
        for message in messages:
            if isinstance(message, SystemMessage):
                message_params["system"] = f'{message_params.get("system", "")}{message.content}\n'
        return {**message_params, **self._default_params, **kwargs}

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if self.streaming:
            completion = ""
            usage_metadata: Optional[UsageMetadata] = None
            generation_info: Dict[str, Any] = {}
            for chunk in self._stream(messages, stop=stop, run_manager=run_manager, **kwargs):
                completion += chunk.text
                generation_info = chunk.generation_info or generation_info
                if isinstance(chunk.message, AIMessageChunk):
                    usage_metadata = chunk.message.usage_metadata
            return ChatResult(
                generations=[
                    ChatGeneration(
                        message=AIMessage(content=completion, additional_kwargs={}, usage_metadata=usage_metadata),
                        generation_info=generation_info or {"finish_reason": "stop"},
                    )
                ],
                llm_output={"token_usage": usage_metadata or {}, "model_name": self.model},
            )

        params = self._convert_prompt_msg_params(messages, **kwargs)
        params["stop"] = stop
        response_payload = self.client.do(**params)
        message = _convert_dict_to_message(response_payload)
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=message,
                    generation_info={"finish_reason": "stop", **response_payload.get("body", {})},
                )
            ],
            llm_output={
                "token_usage": response_payload.get("usage", response_payload.get("body", {}).get("usage", {})),
                "model_name": self.model,
            },
        )

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        params = self._convert_prompt_msg_params(messages, **kwargs)
        params["stop"] = stop
        params["stream"] = True
        for response in self.client.do(**params):
            if not response:
                continue
            message = _convert_dict_to_message(response)
            function_call = message.additional_kwargs.get("function_call", {})
            chunk = ChatGenerationChunk(
                text=response["result"],
                message=AIMessageChunk(
                    content=message.content,
                    role="assistant",
                    additional_kwargs=function_call,
                    usage_metadata=message.usage_metadata,
                ),
                generation_info=message.additional_kwargs,
            )
            if run_manager:
                run_manager.on_llm_new_token(chunk.text, chunk=chunk)
            yield chunk


class QianfanEmbeddingsEndpoint(Embeddings, BaseModel):
    qianfan_ak: Optional[SecretStr] = Field(default=None, alias="api_key")
    qianfan_sk: Optional[SecretStr] = Field(default=None, alias="secret_key")
    chunk_size: int = 16
    model: Optional[str] = Field(default=None)
    endpoint: str = ""
    client: Any = None
    init_kwargs: Dict[str, Any] = Field(default_factory=dict)
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True, protected_namespaces=())

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["qianfan_ak"] = convert_to_secret_str(
            get_from_dict_or_env(values, ["qianfan_ak", "api_key"], "QIANFAN_AK", default="")
        )
        values["qianfan_sk"] = convert_to_secret_str(
            get_from_dict_or_env(values, ["qianfan_sk", "secret_key"], "QIANFAN_SK", default="")
        )

        params = {**values.get("init_kwargs", {}), "model": values.get("model")}
        if values["qianfan_ak"].get_secret_value():
            params["ak"] = values["qianfan_ak"].get_secret_value()
        if values["qianfan_sk"].get_secret_value():
            params["sk"] = values["qianfan_sk"].get_secret_value()
        if values.get("endpoint"):
            params["endpoint"] = values["endpoint"]

        import qianfan

        values["client"] = qianfan.Embedding(**params)
        return values

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        text_chunks = [texts[i : i + self.chunk_size] for i in range(0, len(texts), self.chunk_size)]
        embeddings: List[List[float]] = []
        for chunk in text_chunks:
            response = self.client.do(texts=chunk, **self.model_kwargs)
            embeddings.extend([item["embedding"] for item in response["data"]])
        return embeddings
