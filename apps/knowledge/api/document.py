from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import DefaultResultSerializer
from knowledge.serializers.common import BatchSerializer
from knowledge.serializers.document import DocumentInstanceSerializer, DocumentWebInstanceSerializer, \
    CancelInstanceSerializer, BatchCancelInstanceSerializer, DocumentRefreshSerializer, BatchEditHitHandlingSerializer


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


class DocumentBatchAPI(APIMixin):
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
    def get_request():
        return BatchSerializer

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class DocumentBatchCreateAPI(APIMixin):
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
    def get_request():
        return DocumentInstanceSerializer(many=True)

    @staticmethod
    def get_response():
        return DefaultResultSerializer


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
    def get_request():
        return DocumentInstanceSerializer

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class DocumentReadAPI(APIMixin):
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
            OpenApiParameter(
                name="document_id",
                description="文档id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class DocumentEditAPI(DocumentReadAPI):
    @staticmethod
    def get_request():
        return DocumentInstanceSerializer


class DocumentDeleteAPI(DocumentReadAPI):
    pass


class TableDocumentCreateAPI(APIMixin):
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
            OpenApiParameter(
                name="file",
                description="文件",
                type=OpenApiTypes.BINARY,
                location='query',
                required=False,
            ),
        ]

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class QaDocumentCreateAPI(TableDocumentCreateAPI):
    pass


class WebDocumentCreateAPI(APIMixin):
    @staticmethod
    def get_request():
        return DocumentWebInstanceSerializer


class CancelTaskAPI(DocumentReadAPI):
    @staticmethod
    def get_request():
        return CancelInstanceSerializer


class BatchCancelTaskAPI(DocumentReadAPI):
    @staticmethod
    def get_request():
        return BatchCancelInstanceSerializer


class SyncWebAPI(DocumentReadAPI):
    pass


class RefreshAPI(DocumentReadAPI):
    @staticmethod
    def get_request():
        return DocumentRefreshSerializer


class BatchEditHitHandlingAPI(APIMixin):
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
    def get_request():
        return BatchEditHitHandlingSerializer


class DocumentTreeReadAPI(APIMixin):
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
            OpenApiParameter(
                name="folder_id",
                description="文件夹id",
                type=OpenApiTypes.STR,
                location='query',
                required=True,
            ),
            OpenApiParameter(
                name="user_id",
                description="用户id",
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name="name",
                description="名称",
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name="desc",
                description="描述",
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
        ]


class DocumentSplitPatternAPI(APIMixin):
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
