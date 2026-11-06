from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework import serializers

from common.mixins.api_mixin import APIMixin
from common.result import DefaultResultSerializer, ResultPageSerializer, ResultSerializer
from users.serializers.user_group import SystemUserGroupModelSerializer, SystemUserGroupCreateSerializer


class UserGroupResponse(ResultSerializer):
    def get_data(self):
        return SystemUserGroupModelSerializer()


class CreateUserGroupApi(APIMixin):
    @staticmethod
    def get_request():
        return SystemUserGroupCreateSerializer

    @staticmethod
    def get_response():
        return UserGroupResponse


class DeleteUserGroupApi(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                type=OpenApiTypes.STR,
                description=_("Workspace ID"),
                required=True,
                location=OpenApiParameter.PATH,  # type: ignore
            ),
            OpenApiParameter(
                name="user_group_id",
                description=_("User Group ID"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,  # type: ignore
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return DefaultResultSerializer()


class UserGroupListResponse(ResultSerializer):
    def get_data(self):
        return SystemUserGroupModelSerializer(many=True)


class UserGroupListApi(APIMixin):
    @staticmethod
    def get_response():
        return UserGroupListResponse

    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                type=OpenApiTypes.STR,
                description=_("Workspace ID"),
                required=True,
                location=OpenApiParameter.PATH,  # type: ignore
            )
        ]


class SystemUserGroupUserListSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, label=_("ID"))
    username = serializers.CharField(required=True, label=_("Username"))
    nick_name = serializers.CharField(required=True, label=_("Nickname"))
    system_user_group_relation_id = serializers.CharField(required=False, label=_("Relation ID"))
    source = serializers.CharField(required=False, allow_blank=True, label=_("Source"))
    roles = serializers.ListField(required=False, child=serializers.CharField(required=False), label=_("Roles"))


class SystemUserGroupUserListPageResponse(ResultPageSerializer):
    def get_data(self):
        return SystemUserGroupUserListSerializer(many=True)


class UserGroupListPageResponse(ResultSerializer):
    def get_data(self):
        return SystemUserGroupModelSerializer(many=True)


class UserGroupListPageApi(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                type=OpenApiTypes.STR,
                description=_("Workspace ID"),
                required=True,
                location=OpenApiParameter.PATH,  # type: ignore
            ),
            OpenApiParameter(
                name="user_group_id",
                type=OpenApiTypes.STR,
                description=_("Group ID"),
                required=True,
                location=OpenApiParameter.PATH,  # type: ignore
            ),
            OpenApiParameter(
                name="current_page",
                type=OpenApiTypes.INT,
                description=_("Current page"),
                required=True,
                location=OpenApiParameter.PATH,  # type: ignore
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                description=_("Page size"),
                required=True,
                location=OpenApiParameter.PATH,  # type: ignore
            ),
            OpenApiParameter(
                name="username",
                type=OpenApiTypes.STR,
                description=_("Username"),
                required=False,
                location=OpenApiParameter.QUERY,  # type: ignore
            ),
            OpenApiParameter(
                name="nick_name",
                type=OpenApiTypes.STR,
                description=_("Nickname"),
                required=False,
                location=OpenApiParameter.QUERY,  # type: ignore
            ),
            OpenApiParameter(
                name="role",
                type=OpenApiTypes.STR,
                description=_("Role"),
                required=False,
                location=OpenApiParameter.QUERY,  # type: ignore
            ),
        ]

    @staticmethod
    def get_response():
        return UserGroupListPageResponse


class AddMemberRequest(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.CharField(required=True), required=True, label=_("User IDs"))


class AddMemberApi(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                type=OpenApiTypes.STR,
                description=_("Workspace ID"),
                required=True,
                location=OpenApiParameter.PATH,  # type: ignore
            ),
            OpenApiParameter(
                name="user_group_id",
                description=_("User Group ID"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,  # type: ignore
                required=True,
            ),
        ]

    @staticmethod
    def get_request():
        return AddMemberRequest

    @staticmethod
    def get_response():
        return DefaultResultSerializer()


class RemoveMemberRequest(serializers.Serializer):
    group_relation_ids = serializers.ListField(
        child=serializers.CharField(required=True), required=True, label=_("User group relation IDs")
    )


class RemoveMemberApi(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                type=OpenApiTypes.STR,
                description=_("Workspace ID"),
                required=True,
                location=OpenApiParameter.PATH,  # type: ignore
            ),
            OpenApiParameter(
                name="user_group_id",
                description=_("User Group ID"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,  # type: ignore
                required=True,
            ),
        ]

    @staticmethod
    def get_request():
        return RemoveMemberRequest

    @staticmethod
    def get_response():
        return DefaultResultSerializer()
