# coding=utf-8
import base64
import os
from typing import Dict, Any, List, Optional, Iterator

from docutils.utils import SystemMessage
from langchain_community.chat_models.sparkllm import ChatSparkLLM, _convert_delta_to_message_chunk
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.messages import BaseMessage, ChatMessage, HumanMessage, AIMessage, AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk

from setting.models_provider.base_model_provider import MaxKBBaseModel


class ImageMessage(HumanMessage):
    content: str


def convert_message_to_dict(message: BaseMessage) -> dict:
    message_dict: Dict[str, Any]
    if isinstance(message, ChatMessage):
        message_dict = {"role": "user", "content": message.content}
    elif isinstance(message, ImageMessage):
        message_dict = {"role": "user", "content": message.content, "content_type": "image"}
    elif isinstance(message, HumanMessage):
        message_dict = {"role": "user", "content": message.content}
    elif isinstance(message, AIMessage):
        message_dict = {"role": "assistant", "content": message.content}
        if "function_call" in message.additional_kwargs:
            message_dict["function_call"] = message.additional_kwargs["function_call"]
            # If function call only, content is None not empty string
            if message_dict["content"] == "":
                message_dict["content"] = None
        if "tool_calls" in message.additional_kwargs:
            message_dict["tool_calls"] = message.additional_kwargs["tool_calls"]
            # If tool calls only, content is None not empty string
            if message_dict["content"] == "":
                message_dict["content"] = None
    elif isinstance(message, SystemMessage):
        message_dict = {"role": "system", "content": message.content}
    else:
        raise ValueError(f"Got unknown type {message}")

    return message_dict


class XFSparkImage(MaxKBBaseModel, ChatSparkLLM):
    spark_app_id: str
    spark_api_key: str
    spark_api_secret: str
    spark_api_url: str

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        return XFSparkImage(
            spark_app_id=model_credential.get('spark_app_id'),
            spark_api_key=model_credential.get('spark_api_key'),
            spark_api_secret=model_credential.get('spark_api_secret'),
            spark_api_url=model_credential.get('spark_api_url'),
            **optional_params
        )

    @staticmethod
    def generate_message(prompt: str, image) -> list[BaseMessage]:
        if image is None:
            cwd = os.path.dirname(os.path.abspath(__file__))
            with open(f'{cwd}/img_1.png', 'rb') as f:
                base64_image = base64.b64encode(f.read()).decode("utf-8")
                return [ImageMessage(f'data:image/jpeg;base64,{base64_image}'), HumanMessage(prompt)]
        return [HumanMessage(prompt)]

    def _stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        default_chunk_class = AIMessageChunk

        self.client.arun(
            [convert_message_to_dict(m) for m in messages],
            self.spark_user_id,
            self.model_kwargs,
            streaming=True,
        )
        for content in self.client.subscribe(timeout=self.request_timeout):
            if "data" not in content:
                continue
            delta = content["data"]
            chunk = _convert_delta_to_message_chunk(delta, default_chunk_class)
            cg_chunk = ChatGenerationChunk(message=chunk)
            if run_manager:
                run_manager.on_llm_new_token(str(chunk.content), chunk=cg_chunk)
            yield cg_chunk
