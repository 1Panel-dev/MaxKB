from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from knowledge.serializers.knowledge import KnowledgeBaseCreateRequest, KnowledgeModelSerializer


class KnowledgeCreateResponse(ResultSerializer):
    def get_data(self):
        return KnowledgeModelSerializer()


class KnowledgeBaseCreateAPI(APIMixin):
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
        return KnowledgeBaseCreateRequest

    @staticmethod
    def get_response():
        return KnowledgeCreateResponse


class KnowledgeWebCreateAPI(APIMixin):
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
        return KnowledgeBaseCreateRequest

    @staticmethod
    def get_response():
        return KnowledgeCreateResponse


class KnowledgeTreeReadAPI(APIMixin):
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
