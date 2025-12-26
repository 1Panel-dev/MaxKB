# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： resource_mapping.py
    @date：2025/12/26 14:07
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework import serializers

from common.mixins.api_mixin import APIMixin


class ResourceMappingResponse(serializers.Serializer):
    id = serializers.UUIDField(required=True, label="主键id")
    target_id = serializers.CharField(required=True, label="被关联资源名称")
    target_type = serializers.CharField(required=True, label="被关联资源类型")
    source_id = serializers.CharField(required=True, label="关联资源Id")
    source_type = serializers.CharField(required=True, label="关联资源类型")
    name = serializers.CharField(required=True, label="名称")
    desc = serializers.CharField(required=False, label="描述")
    user_id = serializers.UUIDField(required=True, label="主键id")


class ResourceMappingAPI(APIMixin):

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
                name="source",
                description="资源类型",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="source_id",
                description="资源id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="current_page",
                description=_("Current page"),
                type=OpenApiTypes.INT,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="page_size",
                description=_("Page size"),
                type=OpenApiTypes.INT,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="resource_name",
                description="名称",
                type=OpenApiTypes.STR,
                location='query',
                required=False
            ),

        ]

    @staticmethod
    def get_response():
        return ResourceMappingResponse(many=True)
