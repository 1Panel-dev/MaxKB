# coding=utf-8
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer, DefaultResultSerializer
from tools.serializers.tool import ToolModelSerializer, ToolCreateRequest


class ToolCreateResponse(ResultSerializer):
    def get_data(self):
        return ToolModelSerializer()


class ToolCreateAPI(APIMixin):
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
        return ToolCreateRequest

    @staticmethod
    def get_response():
        return ToolCreateResponse


class ToolReadAPI(APIMixin):
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
                name="tool_id",
                description="工具id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ]

    @staticmethod
    def get_response():
        return ToolCreateResponse


class ToolEditAPI(ToolReadAPI):

    @staticmethod
    def get_request():
        return ToolCreateRequest


class ToolDeleteAPI(ToolReadAPI):
    @staticmethod
    def get_response():
        return DefaultResultSerializer


class ToolTreeReadAPI(APIMixin):
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
                name="module_id",
                description="模块id",
                type=OpenApiTypes.STR,
                location='query',
                required=True,
            )
        ]
