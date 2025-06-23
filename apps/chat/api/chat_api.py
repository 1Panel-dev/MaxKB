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
from chat.serializers.chat_record import HistoryChatRecordModel
from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer, ResultPageSerializer


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


class ApplicationCreateResponse(ResultSerializer):
    def get_data(self):
        return HistoryChatRecordModel(many=True)


class PageApplicationCreateResponse(ResultPageSerializer):
    def get_data(self):
        return HistoryChatRecordModel(many=True)


class HistoricalConversationAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return []

    @staticmethod
    def get_response():
        return ApplicationCreateResponse


class PageHistoricalConversationAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return []

    @staticmethod
    def get_response():
        return PageApplicationCreateResponse
