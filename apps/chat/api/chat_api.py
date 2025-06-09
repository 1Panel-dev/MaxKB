# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： chat_api.py
    @date：2025/6/9 15:23
    @desc:
"""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from chat.serializers.chat import ChatMessageSerializers
from common.mixins.api_mixin import APIMixin


class ChatAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            name="chat_id",
            description="对话id",
            type=OpenApiTypes.STR,
            location='path',
            required=True,
        )]

    @staticmethod
    def get_request():
        return ChatMessageSerializers
