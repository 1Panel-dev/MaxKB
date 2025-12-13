# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_version.py
    @date：2025/6/4 17:33
    @desc:
"""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer, ResultPageSerializer
from knowledge.serializers.knowledge_version import KnowledgeVersionModelSerializer


class KnowledgeListVersionResult(ResultSerializer):
    def get_data(self):
        return KnowledgeVersionModelSerializer(many=True)


class KnowledgePageVersionResult(ResultPageSerializer):
    def get_data(self):
        return KnowledgeVersionModelSerializer(many=True)


class KnowledgeWorkflowVersionResult(ResultSerializer):
    def get_data(self):
        return KnowledgeVersionModelSerializer()


class KnowledgeVersionAPI(APIMixin):
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
                description="knowledge ID",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ]


class KnowledgeVersionOperateAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="knowledge_version_id",
                description="工作流版本id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
            , *KnowledgeVersionAPI.get_parameters()
        ]

    @staticmethod
    def get_response():
        return KnowledgeWorkflowVersionResult


class KnowledgeVersionListAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="name",
                description="Version Name",
                type=OpenApiTypes.STR,
                required=False,
            )
            , *KnowledgeVersionOperateAPI.get_parameters()]

    @staticmethod
    def get_response():
        return KnowledgeListVersionResult


class KnowledgeVersionPageAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return KnowledgeVersionListAPI.get_parameters()

    @staticmethod
    def get_response():
        return KnowledgePageVersionResult
