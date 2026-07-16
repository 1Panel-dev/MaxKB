# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_chat_export_csv.py
    @date：2025/7/14 11:00
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from application.serializers.export_chat_record_csv import ApplicationChatExportCsvSerializer
from common.mixins.api_mixin import APIMixin


class ApplicationChatCsvExportAPI(APIMixin):
    @staticmethod
    def get_request():
        return ApplicationChatExportCsvSerializer

    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description=_("Workspace ID"),
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="application_id",
                description=_("Application ID"),
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="start_time",
                description=_("Start time"),
                type=OpenApiTypes.STR,
                required=True,
            ),
            OpenApiParameter(
                name="end_time",
                description=_("End time"),
                type=OpenApiTypes.STR,
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return None
