# coding=utf-8
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer, DefaultResultSerializer
from tools.serializers.tool import ToolModelSerializer, ToolCreateRequest, ToolDebugRequest


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
                required=False,
            )
        ]


class ToolDebugApi(APIMixin):
    @staticmethod
    def get_request():
        return ToolDebugRequest

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class ToolExportAPI(APIMixin):
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
        return DefaultResultSerializer


class ToolImportAPI(APIMixin):
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
                name='file',
                type=OpenApiTypes.BINARY,
                description='工具文件',
                required=True
            ),
        ]

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class ToolPageAPI(ToolReadAPI):
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
                description="当前页码",
                type=OpenApiTypes.INT,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="page_size",
                description="每页大小",
                type=OpenApiTypes.INT,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="module_id",
                description="模块id",
                type=OpenApiTypes.STR,
                location='query',
                required=True,
            ),
            OpenApiParameter(
                name="tool_type",
                description="工具类型",
                type=OpenApiTypes.STR,
                enum=["CUSTOM", "INTERNAL"],
                location='query',
                required=True,
            ),
            OpenApiParameter(
                name="name",
                description="工具名称",
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
        ]
