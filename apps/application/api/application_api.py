# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application.py
    @date：2025/5/26 16:59
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework import serializers

from application.serializers.application import ApplicationCreateSerializer, ApplicationListResponse, \
    ApplicationImportRequest, ApplicationEditSerializer, TextToSpeechRequest, SpeechToTextRequest, PlayDemoTextRequest
from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer, ResultPageSerializer, DefaultResultSerializer


class ApplicationCreateRequest(ApplicationCreateSerializer.SimplateRequest):
    work_flow = serializers.DictField(required=True, label=_("Workflow Objects"))


class ApplicationCreateResponse(ResultSerializer):
    def get_data(self):
        return ApplicationCreateSerializer.ApplicationResponse()


class ApplicationListResult(ResultSerializer):
    def get_data(self):
        return ApplicationListResponse(many=True)


class ApplicationPageResult(ResultPageSerializer):
    def get_data(self):
        return ApplicationListResponse(many=True)


class ApplicationQueryAPI(APIMixin):
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
            OpenApiParameter(
                name="folder_id",
                description=_("folder id"),
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name="name",
                description=_("Application Name"),
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name="desc",
                description=_("Application Description"),
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name="user_id",
                description=_("User ID"),
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name="publish_status",
                description=_("Publish status") + '(published|unpublished)',
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            )
        ]

    @staticmethod
    def get_response():
        return ApplicationListResult

    @staticmethod
    def get_page_response():
        return ApplicationPageResult


class ApplicationCreateAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description="工作空间id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ]

    @staticmethod
    def get_request():
        return ApplicationCreateRequest

    @staticmethod
    def get_response():
        return ApplicationCreateResponse


class ApplicationImportAPI(APIMixin):
    @staticmethod
    def get_parameters():
        ApplicationCreateAPI.get_parameters()

    @staticmethod
    def get_request():
        return ApplicationImportRequest


class ApplicationOperateAPI(APIMixin):
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
                description="应用id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ]


class ApplicationExportAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return ApplicationOperateAPI.get_parameters()

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class ApplicationEditAPI(APIMixin):
    @staticmethod
    def get_request():
        return ApplicationEditSerializer


class TextToSpeechAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return ApplicationOperateAPI.get_parameters()

    @staticmethod
    def get_request():
        return TextToSpeechRequest

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class SpeechToTextAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return ApplicationOperateAPI.get_parameters()

    @staticmethod
    def get_request():
        return SpeechToTextRequest

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class PlayDemoTextAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return ApplicationOperateAPI.get_parameters()

    @staticmethod
    def get_request():
        return PlayDemoTextRequest

    @staticmethod
    def get_response():
        return DefaultResultSerializer
