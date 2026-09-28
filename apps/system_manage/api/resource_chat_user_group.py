from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from common.mixins.api_mixin import APIMixin
from common.result import ResultPageSerializer
from system_manage.models import UserGroup
from system_manage.serializers.resource_chat_user_group import ResourceChatUserGroupEditSerializer


class ResourceChatUserGroupListAPI(APIMixin):
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
                name="user_group_name",
                description="用户组名",
                type=OpenApiTypes.STR,
                required=False,
            ),
        ]


class ResourceChatUserResultSerializer(serializers.ModelSerializer):
    is_auth = serializers.BooleanField(required=True, label=_("is auth"))

    class Meta:
        model = UserGroup
        fields = "__all__"


class ResourceChatUserGroupEditResult(ResultPageSerializer):
    def get_data(self):
        return ResourceChatUserResultSerializer()


class ResourceChatUserGroupEditAPI(APIMixin):
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
        ]

    @staticmethod
    def get_request():
        return ResourceChatUserGroupEditSerializer

    @staticmethod
    def get_response():
        return
