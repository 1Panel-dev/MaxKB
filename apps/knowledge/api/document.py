from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import DefaultResultSerializer, ResultSerializer
from knowledge.serializers.document import DocumentCreateRequest


class DocumentCreateResponse(ResultSerializer):
    @staticmethod
    def get_data():
        return DefaultResultSerializer()


class DocumentCreateAPI(APIMixin):
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
        return DocumentCreateRequest

    @staticmethod
    def get_response():
        return DocumentCreateResponse
