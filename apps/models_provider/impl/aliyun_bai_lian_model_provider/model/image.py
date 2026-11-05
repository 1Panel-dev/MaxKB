# coding=utf-8
from typing import Dict

from langchain_core.messages import HumanMessage

from common.exception.app_exception import AppApiException
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.impl.base_chat_open_ai import BaseChatOpenAI


class QwenVLChatModel(MaxKBBaseModel, BaseChatOpenAI):
    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        if str(model_name).lower().startswith("qwen-image"):
            raise AppApiException(500, "qwen-image 是图像生成模型，不能作为视觉理解模型使用")
        QwenVLChatModel._validate_api_key(model_credential.get("api_key"))
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        chat_tong_yi = QwenVLChatModel(
            model_name=model_name,
            openai_api_key=model_credential.get("api_key"),
            openai_api_base=model_credential.get("api_base") or "https://dashscope.aliyuncs.com/compatible-mode/v1",
            # stream_options={"include_usage": True},
            streaming=True,
            stream_usage=True,
            **optional_params,
        )
        return chat_tong_yi

    @staticmethod
    def _validate_api_key(api_key):
        try:
            str(api_key).encode("ascii")
        except UnicodeEncodeError as error:
            raise AppApiException(500, "API Key 只能是 ASCII 字符，请检查是否包含中文标点或空格") from error

    def check_auth(self, api_key):
        self._validate_api_key(api_key)
        self.invoke([HumanMessage(content=[{"type": "text", "text": "1"}])])
        return True
