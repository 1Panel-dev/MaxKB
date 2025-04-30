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


class DocumentSplitAPI(APIMixin):
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
                name="file",
                description="文件",
                type=OpenApiTypes.BINARY,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name="limit",
                description="分段长度",
                type=OpenApiTypes.INT,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name="patterns",
                description="分段正则列表",
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name="with_filter",
                description="是否清除特殊字符",
                type=OpenApiTypes.BOOL,
                location='query',
                required=False,
            ),
        ]

