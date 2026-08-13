from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import DefaultResultSerializer, ResultPageSerializer, ResultSerializer
from knowledge.serializers.common import BatchSerializer, BatchMoveSerializer
from knowledge.serializers.common import GenerateRelatedSerializer
from knowledge.serializers.knowledge import (
    KnowledgeBaseCreateRequest,
    KnowledgeModelSerializer,
    KnowledgeEditRequest,
    KnowledgeWebCreateRequest,
    HitTestSerializer,
    KnowledgeImportRequest,
)
from knowledge.serializers.knowledge_sync import KnowledgeSyncLogSerializer, KnowledgeSyncSettingRequest


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
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="knowledge_id",
                description="知识库id",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
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
                location="path",
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
                location="path",
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
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="knowledge_id",
                description="知识库id",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
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
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="folder_id",
                description="文件夹id",
                type=OpenApiTypes.STR,
                location="query",
                required=True,
            ),
            OpenApiParameter(
                name="user_id",
                description="用户id",
                type=OpenApiTypes.STR,
                location="query",
                required=False,
            ),
            OpenApiParameter(
                name="name",
                description="名称",
                type=OpenApiTypes.STR,
                location="query",
                required=False,
            ),
            OpenApiParameter(
                name="desc",
                description="描述",
                type=OpenApiTypes.STR,
                location="query",
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
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="current_page",
                description="当前页码",
                type=OpenApiTypes.INT,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="page_size",
                description="每页条数",
                type=OpenApiTypes.INT,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="folder_id",
                description="文件夹id",
                type=OpenApiTypes.STR,
                location="query",
                required=True,
            ),
            OpenApiParameter(
                name="name",
                description="名称",
                type=OpenApiTypes.STR,
                location="query",
                required=False,
            ),
            OpenApiParameter(
                name="desc",
                description="描述",
                type=OpenApiTypes.STR,
                location="query",
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
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="knowledge_id",
                description="知识库id",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="sync_type",
                description="同步类型 (incremental: 增量同步, replace: 替换同步, complete: 完整同步)",
                type=OpenApiTypes.STR,
                location="query",
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class KnowledgeSyncSettingResponse(ResultSerializer):
    def get_data(self):
        return KnowledgeSyncSettingRequest()


class KnowledgeSyncSettingAPI(SyncWebAPI):
    @staticmethod
    def get_request():
        return KnowledgeSyncSettingRequest

    @staticmethod
    def get_response():
        return KnowledgeSyncSettingResponse


class KnowledgeSyncLogResponse(ResultPageSerializer):
    def get_data(self):
        return KnowledgeSyncLogSerializer(many=True)


class KnowledgeSyncLogAPI(SyncWebAPI):
    @staticmethod
    def get_parameters():
        return [
            *SyncWebAPI.get_parameters()[:2],
            OpenApiParameter(
                name="current_page",
                description="当前页码",
                type=OpenApiTypes.INT,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="page_size",
                description="每页条数",
                type=OpenApiTypes.INT,
                location="path",
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return KnowledgeSyncLogResponse


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
                location="path",
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
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="knowledge_id",
                description="知识库id",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="with_source_file",
                description="是否导出原始文件",
                type=OpenApiTypes.BOOL,
                location="query",
                required=False,
            ),
        ]

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class KnowledgeBatchOperateAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description="工作空间id",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            )
        ]

    @staticmethod
    def get_request():
        return BatchSerializer

    @staticmethod
    def get_move_request():
        return BatchMoveSerializer


class KnowledgeImportAPI(APIMixin):
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
        ]

    @staticmethod
    def get_request():
        return KnowledgeImportRequest

    @staticmethod
    def get_response():
        return DefaultResultSerializer
