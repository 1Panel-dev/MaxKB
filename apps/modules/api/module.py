# coding=utf-8
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer, DefaultResultSerializer
from modules.models.module import ModuleCreateRequest, ModuleEditRequest
from modules.serializers.module import ModuleSerializer


class ModuleCreateResponse(ResultSerializer):
    def get_data(self):
        return ModuleSerializer()


class ModuleCreateAPI(APIMixin):
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
                name="source",
                description="菜单",
                type=OpenApiTypes.STR,
                enum=["APPLICATION", "KNOWLEDGE", "TOOL"],
                location='path',
                required=True,
            )
        ]

    @staticmethod
    def get_request():
        return ModuleCreateRequest

    @staticmethod
    def get_response():
        return ModuleCreateResponse


class ModuleReadAPI(APIMixin):
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
                name="source",
                description="菜单",
                type=OpenApiTypes.STR,
                enum=["APPLICATION", "KNOWLEDGE", "TOOL"],
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="module_id",
                description="模块id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ]

    @staticmethod
    def get_response():
        return ModuleCreateResponse


class ModuleEditAPI(ModuleReadAPI):

    @staticmethod
    def get_request():
        return ModuleEditRequest


class ModuleDeleteAPI(ModuleReadAPI):
    @staticmethod
    def get_response():
        return DefaultResultSerializer


class ModuleTreeReadAPI(APIMixin):
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
                name="source",
                description="菜单",
                type=OpenApiTypes.STR,
                enum=["APPLICATION", "KNOWLEDGE", "TOOL"],
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="name",
                description="名称",
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
        ]
