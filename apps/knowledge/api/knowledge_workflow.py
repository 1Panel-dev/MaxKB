# coding=utf-8
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import DefaultResultSerializer
from knowledge.serializers.knowledge_workflow import KnowledgeWorkflowActionRequestSerializer, \
    KnowledgeWorkflowImportRequest
from knowledge.serializers.knowledge_workflow import KnowledgeWorkflowActionListQuerySerializer


class KnowledgeWorkflowApi(APIMixin):
    pass


class KnowledgeWorkflowVersionApi(APIMixin):
    pass


class KnowledgeWorkflowActionPageApi(APIMixin):
    @staticmethod
    def get_request():
        return KnowledgeWorkflowActionListQuerySerializer


class KnowledgeWorkflowActionApi(APIMixin):
    @staticmethod
    def get_request():
        return KnowledgeWorkflowActionRequestSerializer

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

    class Operate(APIMixin):
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
                    name="knowledge_action_id",
                    description="知识库执行id",
                    type=OpenApiTypes.STR,
                    location='path',
                    required=True,
                )
            ]

class KnowledgeWorkflowExportApi(APIMixin):
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

class KnowledgeWorkflowImportApi(APIMixin):
    @staticmethod
    def get_parameters():
        return KnowledgeWorkflowExportApi.get_parameters()

    @staticmethod
    def get_request():
        return KnowledgeWorkflowImportRequest

    @staticmethod
    def get_response():
        return DefaultResultSerializer
