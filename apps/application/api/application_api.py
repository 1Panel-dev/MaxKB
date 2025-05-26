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

from application.serializers.application import ApplicationCreateSerializer
from common.mixins.api_mixin import APIMixin


class ApplicationCreateRequest(ApplicationCreateSerializer.SimplateRequest):
    work_flow = serializers.DictField(required=True, label=_("Workflow Objects"))


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
        return FolderCreateResponse
