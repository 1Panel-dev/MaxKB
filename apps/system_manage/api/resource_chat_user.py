# coding=utf-8
"""
@project: MaxKB-xpack
@Author：虎虎
@file： resource_chat_user.py
@date：2025/6/5 16:22
@desc:
"""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer, ResultPageSerializer
from system_manage.serializers.resource_chat_user import (
    ResourceChatUserResultSerializer,
    ResourceChatUserEditSerializer,
)


class ResourceChatUserListResult(ResultSerializer):
    def get_data(self):
        return ResourceChatUserResultSerializer(many=True)


class ResourceChatUserPageListResult(ResultPageSerializer):
    def get_data(self):
        return ResourceChatUserResultSerializer(many=True)


class WorkspaceResourceChatUserListAPI(APIMixin):
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
                name="resource_type",
                description="资源类型",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="resource_id",
                description="资源id",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="user_group_id",
                description="用户组id",
                type=OpenApiTypes.STR,
                location="path",
                required=False,
            ),
            OpenApiParameter(
                name="username",
                description="用户名",
                type=OpenApiTypes.STR,
                required=False,
            ),
            OpenApiParameter(
                name="nick_name",
                description="昵称",
                type=OpenApiTypes.STR,
                required=False,
            ),
            OpenApiParameter(
                name="source",
                description="来源",
                type=OpenApiTypes.STR,
                required=False,
            ),
        ]

    @staticmethod
    def get_response():
        return ResourceChatUserListResult


class ResourceChatUserPageAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return WorkspaceResourceChatUserListAPI.get_parameters()

    @staticmethod
    def get_response():
        return ResourceChatUserPageListResult


class EditResourceChatUserAPI(APIMixin):
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
                name="resource_type",
                description="资源类型",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="resource_id",
                description="资源id",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
            ),
            OpenApiParameter(
                name="user_group_id",
                description="用户组id",
                type=OpenApiTypes.STR,
                location="path",
                required=False,
            ),
        ]

    @staticmethod
    def get_request():
        return ResourceChatUserEditSerializer

    @staticmethod
    def get_response():
        pass
