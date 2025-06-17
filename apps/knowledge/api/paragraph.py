from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import DefaultResultSerializer, ResultSerializer
from knowledge.serializers.common import BatchSerializer
from knowledge.serializers.paragraph import ParagraphSerializer, ParagraphBatchGenerateRelatedSerializer
from knowledge.serializers.problem import ProblemSerializer


class ParagraphReadResponse(ResultSerializer):
    @staticmethod
    def get_data():
        return ParagraphSerializer(many=True)


class ParagraphReadAPI(APIMixin):
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
            OpenApiParameter(
                name="title",
                description="标题",
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
            OpenApiParameter(
                name="content",
                description="内容",
                type=OpenApiTypes.STR,
                location='query',
                required=False,
            ),
        ]

    @staticmethod
    def get_response():
        return ParagraphReadResponse


class ParagraphCreateAPI(APIMixin):
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
    def get_request():
        return ParagraphSerializer

    @staticmethod
    def get_response():
        return ParagraphReadResponse


class ParagraphBatchDeleteAPI(ParagraphCreateAPI):
    @staticmethod
    def get_request():
        return BatchSerializer

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class ParagraphBatchGenerateRelatedAPI(ParagraphCreateAPI):
    @staticmethod
    def get_request():
        return ParagraphBatchGenerateRelatedSerializer

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class ParagraphGetAPI(APIMixin):
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
            OpenApiParameter(
                name="paragraph_id",
                description="段落id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
        ]


class ParagraphEditAPI(ParagraphGetAPI):

    @staticmethod
    def get_request():
        return ParagraphSerializer

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class ProblemCreateAPI(ParagraphGetAPI):
    @staticmethod
    def get_request():
        return ProblemSerializer

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class UnAssociationAPI(APIMixin):
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
            OpenApiParameter(
                name="paragraph_id",
                description="段落id",
                type=OpenApiTypes.STR,
                location='query',
                required=True,
            ),
            OpenApiParameter(
                name="problem_id",
                description="问题id",
                type=OpenApiTypes.STR,
                location='query',
                required=True,
            )
        ]


class AssociationAPI(UnAssociationAPI):
    pass


class ParagraphPageAPI(APIMixin):
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
            OpenApiParameter(
                name="paragraph_id",
                description="段落id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="current_page",
                description="当前页",
                type=OpenApiTypes.INT,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="page_size",
                description="每页大小",
                type=OpenApiTypes.INT,
                location='path',
                required=True,
            ),
        ]


class ParagraphMigrateAPI(APIMixin):
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
            OpenApiParameter(
                name="target_knowledge_id",
                description="目标知识库id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="target_document_id",
                description="目标文档id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
        ]

    @staticmethod
    def get_request():
        return BatchSerializer


class ParagraphAdjustOrderAPI(APIMixin):
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
            OpenApiParameter(
                name="paragraph_id",
                description="段落id",
                type=OpenApiTypes.STR,
                location='query',
                required=True,
            ),
            OpenApiParameter(
                name="new_position",
                description="新的顺序",
                type=OpenApiTypes.INT,
                location='query',
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return DefaultResultSerializer
