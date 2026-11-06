# coding=utf-8
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import DefaultResultSerializer, ResultSerializer, ResultPageSerializer
from tools.serializers.tool_workflow import ToolWorkflowImportRequest
from tools.serializers.tool_version import ToolVersionModelSerializer


class ToolWorkflowApi(APIMixin):
    pass


class ToolWorkflowVersionResult(ResultSerializer):
    def get_data(self):
        return ToolVersionModelSerializer()


class ToolWorkflowVersionListResult(ResultSerializer):
    def get_data(self):
        return ToolVersionModelSerializer(many=True)


class ToolWorkflowVersionPageResult(ResultPageSerializer):
    def get_data(self):
        return ToolVersionModelSerializer(many=True)


class ToolWorkflowVersionApi(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description="工作空间id",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="tool_id",
                description="工具id",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
        ]


class ToolWorkflowVersionListApi(ToolWorkflowVersionApi):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="name",
                description="Version Name",
                type=OpenApiTypes.STR,
                required=False,
            ),
            *ToolWorkflowVersionApi.get_parameters(),
        ]

    @staticmethod
    def get_response():
        return ToolWorkflowVersionListResult


class ToolWorkflowVersionPageApi(ToolWorkflowVersionListApi):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="current_page",
                description="当前页码",
                type=OpenApiTypes.INT,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="page_size",
                description="每页大小",
                type=OpenApiTypes.INT,
                location="path",
                required=True,
            ),
            *ToolWorkflowVersionListApi.get_parameters(),
        ]

    @staticmethod
    def get_response():
        return ToolWorkflowVersionPageResult


class ToolWorkflowVersionOperateApi(ToolWorkflowVersionApi):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="tool_version_id",
                description="工具版本id",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
            *ToolWorkflowVersionApi.get_parameters(),
        ]

    @staticmethod
    def get_response():
        return ToolWorkflowVersionResult


class ToolWorkflowExportApi(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description="工作空间id",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="tool_id",
                description="工具id",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class ToolWorkflowImportApi(APIMixin):
    @staticmethod
    def get_parameters():
        return ToolWorkflowExportApi.get_parameters()

    @staticmethod
    def get_request():
        return ToolWorkflowImportRequest

    @staticmethod
    def get_response():
        return DefaultResultSerializer
