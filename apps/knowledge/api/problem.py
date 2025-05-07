from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import DefaultResultSerializer
from knowledge.serializers.problem import ProblemBatchSerializer, \
    ProblemBatchDeleteSerializer, BatchAssociation


class ProblemReadAPI(APIMixin):
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
                name="knowledge_id",
                description="知识库id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class ProblemBatchCreateAPI(ProblemReadAPI):
    @staticmethod
    def get_request():
        return ProblemBatchSerializer


class BatchAssociationAPI(ProblemReadAPI):
    @staticmethod
    def get_request():
        return BatchAssociation


class BatchDeleteAPI(ProblemReadAPI):
    @staticmethod
    def get_request():
        return ProblemBatchDeleteSerializer
