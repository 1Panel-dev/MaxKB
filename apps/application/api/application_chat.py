# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_chat.py
    @date：2025/6/10 13:54
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from application.serializers.application_chat import ApplicationChatQuerySerializers, \
    ApplicationChatResponseSerializers, ApplicationChatRecordExportRequest
from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer, ResultPageSerializer


class ApplicationChatListResponseSerializers(ResultSerializer):
    def get_data(self):
        return ApplicationChatResponseSerializers(many=True)


class ApplicationChatPageResponseSerializers(ResultPageSerializer):
    def get_data(self):
        return ApplicationChatResponseSerializers(many=True)


class ApplicationChatQueryAPI(APIMixin):
    @staticmethod
    def get_request():
        return ApplicationChatQuerySerializers

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
                description="application ID",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ), OpenApiParameter(
                name="start_time",
                description="start Time",
                type=OpenApiTypes.STR,
                required=True,
            ),
            OpenApiParameter(
                name="end_time",
                description="end Time",
                type=OpenApiTypes.STR,
                required=True,
            ),
            OpenApiParameter(
                name="abstract",
                description="summary",
                type=OpenApiTypes.STR,
                required=False,
            ),
            OpenApiParameter(
                name="min_star",
                description=_("Minimum number of likes"),
                type=OpenApiTypes.INT,
                required=False,
            ),
            OpenApiParameter(
                name="min_trample",
                description=_("Minimum number of clicks"),
                type=OpenApiTypes.INT,
                required=False,
            ),
            OpenApiParameter(
                name="comparer",
                description=_("Comparator"),
                type=OpenApiTypes.STR,
                required=False,
            ),
        ]

    @staticmethod
    def get_response():
        return ApplicationChatListResponseSerializers


class ApplicationChatQueryPageAPI(APIMixin):
    @staticmethod
    def get_request():
        return ApplicationChatQueryAPI.get_request()

    @staticmethod
    def get_parameters():
        return [
            *ApplicationChatQueryAPI.get_parameters(),
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
            ),

        ]

    @staticmethod
    def get_response():
        return ApplicationChatPageResponseSerializers


class ApplicationChatExportAPI(APIMixin):
    @staticmethod
    def get_request():
        return ApplicationChatRecordExportRequest

    @staticmethod
    def get_parameters():
        return ApplicationChatQueryAPI.get_parameters()

    @staticmethod
    def get_response():
        return None
