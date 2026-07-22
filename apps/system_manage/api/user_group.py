from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from rest_framework import serializers

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer, DefaultResultSerializer
from system_manage.serializers.chat_user import UserGroupCreateSerializer, UserGroupModelSerializer
from django.utils.translation import gettext_lazy as _


class UserGroupResponse(ResultSerializer):
    def get_data(self):
        return UserGroupModelSerializer()


class CreateUserGroupApi(APIMixin):
    @staticmethod
    def get_request():
        return UserGroupCreateSerializer

    @staticmethod
    def get_response():
        return UserGroupResponse


class DeleteUserGroupApi(APIMixin):
    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            name="user_group_id",
            description=_("User Group ID"),
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
        )]

    @staticmethod
    def get_response():
        return DefaultResultSerializer()


class UserGroupListResponse(ResultSerializer):
    def get_data(self):
        return UserGroupModelSerializer(many=True)


class UserGroupListApi(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name='user_group_id',
                type=OpenApiTypes.STR,
                description=_('Group ID'),
                required=True,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name='current_page',
                type=OpenApiTypes.INT,
                description=_('Current page'),
                required=True,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                description=_('Page size'),
                required=True,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name='username',
                type=OpenApiTypes.STR,
                description=_('Username'),
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='nick_name',
                type=OpenApiTypes.STR,
                description=_('Nickname'),
                required=False,
                location=OpenApiParameter.QUERY,
            ),
        ]

    @staticmethod
    def get_response():
        return UserGroupListResponse


class AddMemberRequest(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.CharField(required=True),
        required=True,
        label=_('User IDs')
    )


class AddMemberApi(APIMixin):
    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            name="user_group_id",
            description=_("User Group ID"),
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
        )]

    @staticmethod
    def get_request():
        return AddMemberRequest


class RemoveMemberRequest(serializers.Serializer):
    group_relation_ids = serializers.ListField(
        child=serializers.CharField(required=True),
        required=True,
        label=_('User group relation IDs')
    )


class RemoveMemberApi(APIMixin):
    @staticmethod
    def get_request():
        return RemoveMemberRequest
