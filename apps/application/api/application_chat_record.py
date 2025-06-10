# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_chat_record.py
    @date：2025/6/10 15:19
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from application.serializers.application_chat_record import ApplicationChatRecordAddKnowledgeSerializer, \
    ApplicationChatRecordImproveInstanceSerializer
from common.mixins.api_mixin import APIMixin


class ApplicationChatRecordQueryAPI(APIMixin):
    @staticmethod
    def get_response():
        pass

    @staticmethod
    def get_request():
        pass

    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description="工作空间id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="application_id",
                description="Application ID",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="chat_id",
                description=_("Chat ID"),
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="order_asc",
                description=_("Is it in order"),
                type=OpenApiTypes.BOOL,
                required=True,
            )
        ]


class ApplicationChatRecordPageQueryAPI(APIMixin):
    @staticmethod
    def get_response():
        pass

    @staticmethod
    def get_request():
        pass

    @staticmethod
    def get_parameters():
        return [*ApplicationChatRecordQueryAPI.get_parameters(),
                OpenApiParameter(
                    name="current_page",
                    description=_("Current page"),
                    type=OpenApiTypes.INT,
                    location='path',
                    required=True,
                ),
                OpenApiParameter(
                    name="page_size",
                    description=_("Page size"),
                    type=OpenApiTypes.INT,
                    location='path',
                    required=True,
                )]


class ApplicationChatRecordImproveParagraphAPI(APIMixin):
    @staticmethod
    def get_response():
        pass

    @staticmethod
    def get_request():
        return ApplicationChatRecordImproveInstanceSerializer

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
                name="application_id",
                description="Application ID",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="chat_id",
                description=_("Chat ID"),
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="chat_record_id",
                description=_("Chat Record ID"),
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="knowledge_id",
                description=_("Knowledge ID"),
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="document_id",
                description=_("Document ID"),
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ]

    class Operate(APIMixin):
        @staticmethod
        def get_parameters():
            return [*ApplicationChatRecordImproveParagraphAPI.get_parameters(), OpenApiParameter(
                name="paragraph_id",
                description=_("Paragraph ID"),
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )]


class ApplicationChatRecordAddKnowledgeAPI(APIMixin):
    @staticmethod
    def get_request():
        return ApplicationChatRecordAddKnowledgeSerializer

    @staticmethod
    def get_response():
        return None

    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description="工作空间id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="application_id",
                description="Application ID",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )]
