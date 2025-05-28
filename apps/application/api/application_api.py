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
    ApplicationQueryRequest
from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer, ResultPageSerializer


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
