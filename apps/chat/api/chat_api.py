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

from application.serializers.application_chat_record import ChatRecordSerializerModel
from chat.serializers.chat import ChatMessageSerializers, GeneratePromptSerializers
from chat.serializers.chat_record import HistoryChatModel, EditAbstractSerializer
from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer, ResultPageSerializer, DefaultResultSerializer


class PromptGenerateAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            name="workspace_id",
            description="工作空间id",
            type=OpenApiTypes.STR,
            location='path',
            required=True,
        ),
            OpenApiParameter(
                name="model_id",
                description="模型id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
        ),
            OpenApiParameter(
                name="application_id",
                description="应用id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
        ]

    @staticmethod
    def get_request():
        return GeneratePromptSerializers


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
        return HistoryChatModel(many=True)


class PageApplicationCreateResponse(ResultPageSerializer):
    def get_data(self):
        return HistoryChatModel(many=True)


class ApplicationRecordResponse(ResultSerializer):
    def get_data(self):
        return ChatRecordSerializerModel(many=True)


class PageApplicationRecordResponse(ResultPageSerializer):
    def get_data(self):
        return ChatRecordSerializerModel(many=True)


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


class HistoricalConversationOperateAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            name="chat_id",
            description="对话id",
            type=OpenApiTypes.STR,
            location='path',
            required=True
        )]

    @staticmethod
    def get_request():
        return EditAbstractSerializer

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class HistoricalConversationRecordAPI(APIMixin):
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
    def get_response():
        return ApplicationRecordResponse


class PageHistoricalConversationRecordAPI(APIMixin):
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
    def get_response():
        return PageApplicationRecordResponse
