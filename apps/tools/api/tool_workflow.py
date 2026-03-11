# coding=utf-8
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import DefaultResultSerializer
from tools.serializers.tool_workflow import ToolWorkflowImportRequest


class ToolWorkflowApi(APIMixin):
    pass


class ToolWorkflowVersionApi(APIMixin):
    pass


class ToolWorkflowExportApi(APIMixin):
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
