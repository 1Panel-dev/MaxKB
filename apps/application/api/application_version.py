# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_version.py
    @date：2025/6/4 17:33
    @desc:
"""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from application.serializers.application_version import ApplicationVersionModelSerializer
from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer, PageDataResponse, ResultPageSerializer


class ApplicationListVersionResult(ResultSerializer):
    def get_data(self):
        return ApplicationVersionModelSerializer(many=True)


class ApplicationPageVersionResult(ResultPageSerializer):
    def get_data(self):
        return ApplicationVersionModelSerializer(many=True)


class ApplicationWorkflowVersionResult(ResultSerializer):
    def get_data(self):
        return ApplicationVersionModelSerializer()


class ApplicationVersionAPI(APIMixin):
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
            )
        ]


class ApplicationVersionOperateAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="application_version_id",
                description="工作流版本id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
            , *ApplicationVersionAPI.get_parameters()
        ]

    @staticmethod
    def get_response():
        return ApplicationWorkflowVersionResult


class ApplicationVersionListAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="name",
                description="Version Name",
                type=OpenApiTypes.STR,
                required=False,
            )
            , *ApplicationVersionAPI.get_parameters()]

    @staticmethod
    def get_response():
        return ApplicationListVersionResult


class ApplicationVersionPageAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return ApplicationVersionListAPI.get_parameters()

    @staticmethod
    def get_response():
        return ApplicationPageVersionResult
