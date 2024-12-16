# coding=utf-8

from typing import Dict

from langchain_community.chat_models import ChatOpenAI

from setting.models_provider.base_model_provider import MaxKBBaseModel


class QwenVLChatModel(MaxKBBaseModel, ChatOpenAI):

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = MaxKBBaseModel.filter_optional_params(model_kwargs)
        chat_tong_yi = QwenVLChatModel(
            model_name=model_name,
            openai_api_key=model_credential.get('api_key'),
            openai_api_base='https://dashscope.aliyuncs.com/compatible-mode/v1',
            # stream_options={"include_usage": True},
            streaming=True,
            model_kwargs=optional_params,
        )
        return chat_tong_yi
