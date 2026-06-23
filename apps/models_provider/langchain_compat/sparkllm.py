import base64
import hashlib
import hmac
import json
import logging
import queue
import threading
from datetime import datetime
from queue import Queue
from time import mktime
from typing import Any, Dict, Generator, Iterator, List, Mapping, Optional, Type, cast
from urllib.parse import urlencode, urlparse, urlunparse
from wsgiref.handlers import format_date_time

import numpy as np
import requests
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel, generate_from_stream
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    BaseMessageChunk,
    ChatMessage,
    ChatMessageChunk,
    FunctionMessageChunk,
    HumanMessage,
    HumanMessageChunk,
    SystemMessage,
    ToolMessageChunk,
)
from langchain_core.output_parsers.openai_tools import make_invalid_tool_call, parse_tool_call
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.utils import get_from_dict_or_env, get_pydantic_field_names
from langchain_core.utils.pydantic import get_fields
from numpy import ndarray
from pydantic import BaseModel, ConfigDict, Field, model_validator

logger = logging.getLogger(__name__)

SPARK_API_URL = "wss://spark-api.xf-yun.com/v3.5/chat"
SPARK_LLM_DOMAIN = "generalv3.5"


def convert_message_to_dict(message: BaseMessage) -> dict:
    message_dict: Dict[str, Any]
    if isinstance(message, ChatMessage):
        message_dict = {"role": "user", "content": message.content}
    elif isinstance(message, HumanMessage):
        message_dict = {"role": "user", "content": message.content}
    elif isinstance(message, AIMessage):
        message_dict = {"role": "assistant", "content": message.content}
        if "function_call" in message.additional_kwargs:
            message_dict["function_call"] = message.additional_kwargs["function_call"]
            if message_dict["content"] == "":
                message_dict["content"] = None
        if "tool_calls" in message.additional_kwargs:
            message_dict["tool_calls"] = message.additional_kwargs["tool_calls"]
            if message_dict["content"] == "":
                message_dict["content"] = None
    elif isinstance(message, SystemMessage):
        message_dict = {"role": "system", "content": message.content}
    else:
        raise ValueError(f"Got unknown type {message}")
    return message_dict


def convert_dict_to_message(_dict: Mapping[str, Any]) -> BaseMessage:
    msg_role = _dict["role"]
    msg_content = _dict["content"]
    if msg_role == "user":
        return HumanMessage(content=msg_content)
    if msg_role == "assistant":
        invalid_tool_calls = []
        additional_kwargs: Dict[str, Any] = {}
        if function_call := _dict.get("function_call"):
            additional_kwargs["function_call"] = dict(function_call)
        tool_calls = []
        if raw_tool_calls := _dict.get("tool_calls"):
            additional_kwargs["tool_calls"] = raw_tool_calls
            for raw_tool_call in raw_tool_calls:
                try:
                    tool_calls.append(parse_tool_call(raw_tool_call, return_id=True))
                except Exception as exc:
                    invalid_tool_calls.append(make_invalid_tool_call(raw_tool_call, str(exc)))
        else:
            additional_kwargs = {}
        return AIMessage(
            content=msg_content or "",
            additional_kwargs=additional_kwargs,
            tool_calls=tool_calls,
            invalid_tool_calls=invalid_tool_calls,
        )
    if msg_role == "system":
        return SystemMessage(content=msg_content)
    return ChatMessage(content=msg_content, role=msg_role)


def _convert_delta_to_message_chunk(
    _dict: Mapping[str, Any], default_class: Type[BaseMessageChunk]
) -> BaseMessageChunk:
    msg_role = cast(str, _dict.get("role"))
    msg_content = cast(str, _dict.get("content") or "")
    additional_kwargs: Dict[str, Any] = {}
    if _dict.get("function_call"):
        function_call = dict(_dict["function_call"])
        if "name" in function_call and function_call["name"] is None:
            function_call["name"] = ""
        additional_kwargs["function_call"] = function_call
    if _dict.get("tool_calls"):
        additional_kwargs["tool_calls"] = _dict["tool_calls"]
    if msg_role == "user" or default_class == HumanMessageChunk:
        return HumanMessageChunk(content=msg_content)
    if msg_role == "assistant" or default_class == AIMessageChunk:
        return AIMessageChunk(content=msg_content, additional_kwargs=additional_kwargs)
    if msg_role == "function" or default_class == FunctionMessageChunk:
        return FunctionMessageChunk(content=msg_content, name=_dict["name"])
    if msg_role == "tool" or default_class == ToolMessageChunk:
        return ToolMessageChunk(content=msg_content, tool_call_id=_dict["tool_call_id"])
    if msg_role or default_class == ChatMessageChunk:
        return ChatMessageChunk(content=msg_content, role=msg_role)
    return default_class(content=msg_content)  # type: ignore[call-arg]


class ChatSparkLLM(BaseChatModel):
    client: Any = None
    spark_app_id: Optional[str] = Field(default=None, alias="app_id")
    spark_api_key: Optional[str] = Field(default=None, alias="api_key")
    spark_api_secret: Optional[str] = Field(default=None, alias="api_secret")
    spark_api_url: Optional[str] = Field(default=None, alias="api_url")
    spark_llm_domain: Optional[str] = Field(default=None, alias="model")
    spark_user_id: str = "lc_user"
    streaming: bool = False
    request_timeout: int = Field(30, alias="timeout")
    temperature: float = 0.5
    top_k: int = 4
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def build_extra(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        extra = values.get("model_kwargs", {})
        all_required_field_names = get_pydantic_field_names(cls)
        for field_name in list(values):
            if field_name in extra:
                raise ValueError(f"Found {field_name} supplied twice.")
            if field_name not in all_required_field_names:
                extra[field_name] = values.pop(field_name)
        invalid_model_kwargs = all_required_field_names.intersection(extra.keys())
        if invalid_model_kwargs:
            raise ValueError(
                f"Parameters {invalid_model_kwargs} should be specified explicitly. "
                "Instead they were passed in as part of `model_kwargs` parameter."
            )
        values["model_kwargs"] = extra
        return values

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["spark_app_id"] = get_from_dict_or_env(values, ["spark_app_id", "app_id"], "IFLYTEK_SPARK_APP_ID")
        values["spark_api_key"] = get_from_dict_or_env(
            values, ["spark_api_key", "api_key"], "IFLYTEK_SPARK_API_KEY"
        )
        values["spark_api_secret"] = get_from_dict_or_env(
            values, ["spark_api_secret", "api_secret"], "IFLYTEK_SPARK_API_SECRET"
        )
        values["spark_api_url"] = get_from_dict_or_env(
            values, "spark_api_url", "IFLYTEK_SPARK_API_URL", SPARK_API_URL
        )
        values["spark_llm_domain"] = get_from_dict_or_env(
            values, "spark_llm_domain", "IFLYTEK_SPARK_LLM_DOMAIN", SPARK_LLM_DOMAIN
        )

        model_kwargs = values.setdefault("model_kwargs", {})
        field_values = {name: field.default for name, field in get_fields(cls).items() if field.default is not None}
        field_values.update(values)
        model_kwargs["temperature"] = field_values.get("temperature")
        model_kwargs["top_k"] = field_values.get("top_k")

        values["client"] = _SparkLLMClient(
            app_id=values["spark_app_id"],
            api_key=values["spark_api_key"],
            api_secret=values["spark_api_secret"],
            api_url=values["spark_api_url"],
            spark_domain=values["spark_llm_domain"],
            model_kwargs=model_kwargs,
        )
        return values

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        default_chunk_class = AIMessageChunk
        self.client.arun(
            [convert_message_to_dict(message) for message in messages],
            self.spark_user_id,
            self.model_kwargs,
            streaming=True,
        )
        for content in self.client.subscribe(timeout=self.request_timeout):
            if "data" not in content:
                continue
            delta = content["data"]
            generation_info = {}
            if "reasoning_content" in delta:
                generation_info["reasoning_content"] = delta.pop("reasoning_content")
            chunk = _convert_delta_to_message_chunk(delta, default_chunk_class)
            generation_chunk = ChatGenerationChunk(message=chunk, generation_info=generation_info or None)
            if run_manager:
                run_manager.on_llm_new_token(str(chunk.content), chunk=generation_chunk)
            yield generation_chunk

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        stream: Optional[bool] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if stream or self.streaming:
            return generate_from_stream(self._stream(messages=messages, stop=stop, run_manager=run_manager, **kwargs))

        self.client.arun(
            [convert_message_to_dict(message) for message in messages],
            self.spark_user_id,
            self.model_kwargs,
            False,
        )
        completion: Dict[str, Any] = {}
        llm_output: Dict[str, Any] = {}
        for content in self.client.subscribe(timeout=self.request_timeout):
            if "usage" in content:
                llm_output["token_usage"] = content["usage"]
            if "data" in content:
                completion = content["data"]

        generation_info = {}
        if "reasoning_content" in completion:
            generation_info["reasoning_content"] = completion.pop("reasoning_content")
        return ChatResult(
            generations=[ChatGeneration(message=convert_dict_to_message(completion), generation_info=generation_info or None)],
            llm_output=llm_output,
        )

    @property
    def _llm_type(self) -> str:
        return "spark-llm-chat"


class _SparkLLMClient:
    def __init__(
        self,
        app_id: str,
        api_key: str,
        api_secret: str,
        api_url: Optional[str] = None,
        spark_domain: Optional[str] = None,
        model_kwargs: Optional[dict] = None,
    ):
        import websocket

        self.websocket_client = websocket
        self.api_url = api_url or SPARK_API_URL
        self.app_id = app_id
        self.model_kwargs = model_kwargs
        self.spark_domain = spark_domain or SPARK_LLM_DOMAIN
        self.queue: Queue[Dict[str, Any]] = Queue()
        self.blocking_message = {"content": "", "role": "assistant"}
        self.api_key = api_key
        self.api_secret = api_secret

    @staticmethod
    def _create_url(api_url: str, api_key: str, api_secret: str) -> str:
        date = format_date_time(mktime(datetime.now().timetuple()))
        parsed_url = urlparse(api_url)
        host = parsed_url.netloc
        path = parsed_url.path
        signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
        signature_sha = hmac.new(
            api_secret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding="utf-8")
        authorization_origin = (
            f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", '
            f'signature="{signature_sha_base64}"'
        )
        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode(encoding="utf-8")
        return urlunparse(
            (
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                urlencode({"authorization": authorization, "date": date, "host": host}),
                parsed_url.fragment,
            )
        )

    def run(
        self,
        messages: List[Dict[str, Any]],
        user_id: str,
        model_kwargs: Optional[dict] = None,
        streaming: bool = False,
    ) -> None:
        self.websocket_client.enableTrace(False)
        ws = self.websocket_client.WebSocketApp(
            self._create_url(self.api_url, self.api_key, self.api_secret),
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open,
        )
        ws.messages = messages  # type: ignore[attr-defined]
        ws.user_id = user_id  # type: ignore[attr-defined]
        ws.model_kwargs = self.model_kwargs if model_kwargs is None else model_kwargs  # type: ignore[attr-defined]
        ws.streaming = streaming  # type: ignore[attr-defined]
        ws.run_forever()

    def arun(
        self,
        messages: List[Dict[str, Any]],
        user_id: str,
        model_kwargs: Optional[dict] = None,
        streaming: bool = False,
    ) -> threading.Thread:
        thread = threading.Thread(target=self.run, args=(messages, user_id, model_kwargs, streaming))
        thread.start()
        return thread

    def on_error(self, ws: Any, error: Optional[Any]) -> None:
        self.queue.put({"error": error})
        ws.close()

    def on_close(self, ws: Any, close_status_code: int, close_reason: str) -> None:
        logger.debug({"close_status_code": close_status_code, "close_reason": close_reason})
        self.queue.put({"done": True})

    def on_open(self, ws: Any) -> None:
        self.blocking_message = {"content": "", "role": "assistant"}
        ws.send(json.dumps(self.gen_params(messages=ws.messages, user_id=ws.user_id, model_kwargs=ws.model_kwargs)))

    def on_message(self, ws: Any, message: str) -> None:
        data = json.loads(message)
        code = data["header"]["code"]
        if code != 0:
            self.queue.put({"error": f"Code: {code}, Error: {data['header']['message']}"})
            ws.close()
            return

        choices = data["payload"]["choices"]
        status = choices["status"]
        text_chunk = choices["text"][0]
        content = text_chunk.get("content", "")
        if ws.streaming:
            self.queue.put({"data": text_chunk})
        else:
            self.blocking_message["content"] += content
            if "reasoning_content" in text_chunk:
                self.blocking_message["reasoning_content"] = text_chunk["reasoning_content"]
        if status == 2:
            if not ws.streaming:
                self.queue.put({"data": self.blocking_message})
            usage_data = data.get("payload", {}).get("usage", {}).get("text", {})
            self.queue.put({"usage": usage_data})
            ws.close()

    def gen_params(
        self, messages: List[Dict[str, Any]], user_id: str, model_kwargs: Optional[dict] = None
    ) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "header": {"app_id": self.app_id, "uid": user_id},
            "parameter": {"chat": {"domain": self.spark_domain}},
            "payload": {"message": {"text": messages}},
        }
        if model_kwargs:
            data["parameter"]["chat"].update(model_kwargs)
        return data

    def subscribe(self, timeout: Optional[int] = 30) -> Generator[Dict[str, Any], None, None]:
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty as exc:
                raise TimeoutError(f"SparkLLMClient wait LLM api response timeout {timeout} seconds") from exc
            if "error" in content:
                raise ConnectionError(content["error"])
            if "usage" in content:
                yield content
                continue
            if "done" in content or "data" not in content:
                break
            yield content


class Url:
    def __init__(self, host: str, path: str, schema: str) -> None:
        self.host = host
        self.path = path
        self.schema = schema


class SparkLLMTextEmbeddings(BaseModel, Embeddings):
    spark_app_id: Optional[str] = Field(default=None, alias="app_id")
    spark_api_key: Optional[str] = Field(default=None, alias="api_key")
    spark_api_secret: Optional[str] = Field(default=None, alias="api_secret")
    base_url: str = "https://emb-cn-huabei-1.xf-yun.com/"
    domain: str = "para"

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        values["spark_app_id"] = get_from_dict_or_env(values, ["spark_app_id", "app_id"], "SPARK_APP_ID")
        values["spark_api_key"] = get_from_dict_or_env(values, ["spark_api_key", "api_key"], "SPARK_API_KEY")
        values["spark_api_secret"] = get_from_dict_or_env(
            values, ["spark_api_secret", "api_secret"], "SPARK_API_SECRET"
        )
        return values

    def _embed(self, texts: List[str], host: str) -> List[List[float]]:
        url = self._assemble_ws_auth_url(
            request_url=host,
            method="POST",
            api_key=self.spark_api_key or "",
            api_secret=self.spark_api_secret or "",
        )
        embedding_result: List[List[float]] = []
        for text in texts:
            response = requests.post(
                url,
                json=self._get_body(self.spark_app_id or "", {"messages": [{"content": text, "role": "user"}]}),
                headers={"content-type": "application/json"},
                timeout=30,
            )
            response.raise_for_status()
            parsed = self._parser_message(response.text)
            if parsed is None:
                raise ValueError("Failed to parse Spark embedding response")
            embedding_result.append(parsed.tolist())
        return embedding_result

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts, self.base_url)

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text], self.base_url)[0]

    @staticmethod
    def _assemble_ws_auth_url(
        request_url: str, method: str = "GET", api_key: str = "", api_secret: str = ""
    ) -> str:
        url = SparkLLMTextEmbeddings._parse_url(request_url)
        date = format_date_time(mktime(datetime.now().timetuple()))
        signature_origin = f"host: {url.host}\ndate: {date}\n{method} {url.path} HTTP/1.1"
        signature_sha = hmac.new(
            api_secret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        signature_sha_str = base64.b64encode(signature_sha).decode(encoding="utf-8")
        authorization_origin = (
            'api_key="%s", algorithm="%s", headers="%s", signature="%s"'
            % (api_key, "hmac-sha256", "host date request-line", signature_sha_str)
        )
        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode(encoding="utf-8")
        return request_url + "?" + urlencode({"host": url.host, "date": date, "authorization": authorization})

    @staticmethod
    def _parse_url(request_url: str) -> Url:
        stidx = request_url.index("://")
        host = request_url[stidx + 3 :]
        schema = request_url[: stidx + 3]
        edidx = host.index("/")
        if edidx <= 0:
            raise AssembleHeaderException("invalid request url:" + request_url)
        return Url(host[:edidx], host[edidx:], schema)

    def _get_body(self, appid: str, text: dict) -> Dict[str, Any]:
        return {
            "header": {"app_id": appid, "uid": "39769795890", "status": 3},
            "parameter": {"emb": {"domain": self.domain, "feature": {"encoding": "utf8"}}},
            "payload": {"messages": {"text": base64.b64encode(json.dumps(text).encode("utf-8")).decode()}},
        }

    @staticmethod
    def _parser_message(message: str) -> Optional[ndarray]:
        data = json.loads(message)
        code = data["header"]["code"]
        if code != 0:
            logger.warning("Request error: %s, %s", code, data)
            return None
        text_data = base64.b64decode(data["payload"]["feature"]["text"])
        float_dtype = np.dtype(np.float32).newbyteorder("<")
        text = np.frombuffer(text_data, dtype=float_dtype)
        return text[:2560] if len(text) > 2560 else text


class AssembleHeaderException(Exception):
    def __init__(self, msg: str) -> None:
        self.message = msg
