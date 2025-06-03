from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer, DefaultResultSerializer
from knowledge.serializers.common import GenerateRelatedSerializer
from knowledge.serializers.knowledge import KnowledgeBaseCreateRequest, KnowledgeModelSerializer, KnowledgeEditRequest, \
    KnowledgeWebCreateRequest, HitTestSerializer


class KnowledgeCreateResponse(ResultSerializer):
    def get_data(self):
        return KnowledgeModelSerializer()


class KnowledgeReadAPI(APIMixin):
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
            )
        ]

    @staticmethod
    def get_response():
        return KnowledgeCreateResponse


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
        return KnowledgeWebCreateRequest

    @staticmethod
    def get_response():
        return KnowledgeCreateResponse


class KnowledgeEditAPI(APIMixin):
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
            )
        ]

    @staticmethod
    def get_request():
        return KnowledgeEditRequest

    @staticmethod
    def get_response():
        return KnowledgeCreateResponse


class KnowledgeTreeReadAPI(KnowledgeReadAPI):
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


class KnowledgePageAPI(KnowledgeReadAPI):
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
                description="每页条数",
                type=OpenApiTypes.INT,
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


class SyncWebAPI(APIMixin):
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


class GenerateRelatedAPI(SyncWebAPI):
    @staticmethod
    def get_request():
        return GenerateRelatedSerializer


class HitTestAPI(SyncWebAPI):
    @staticmethod
    def get_request():
        return HitTestSerializer


class EmbeddingAPI(SyncWebAPI):
    pass


class GetModelAPI(SyncWebAPI):
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
        ]

    @staticmethod
    def get_response():
        return DefaultResultSerializer

class KnowledgeExportAPI(APIMixin):
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