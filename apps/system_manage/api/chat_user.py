# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： user.py
    @date：2025/4/14 19:23
    @desc:
"""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from users.serializers.user import CreateUserSerializer
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from system_manage.serializers.chat_user import ChatUserInstanceSerializer, ChatUserSerializer


class ChatUserResponse(ResultSerializer):
    def get_data(self):
        return ChatUserInstanceSerializer()


class CreateChatUserRequestSerializer(CreateUserSerializer):
    user_group_ids = serializers.ListField(
        child=serializers.CharField(required=True),
        required=True,
        label=_('User Group IDs')
    )


class ChatUserAPI(APIMixin):

    @staticmethod
    def get_response():
        return ChatUserResponse

    @staticmethod
    def get_request():
        return CreateChatUserRequestSerializer

    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            name="user_id",
            description=_('User ID'),
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
        )]


class BatchAddGroupApi(APIMixin):

    @staticmethod
    def get_request():
        return ChatUserSerializer.BatchAddGroup


class UserPasswordResponse(APIMixin):

    @staticmethod
    def get_response():
        return PasswordResponse


class Password(serializers.Serializer):
    password = serializers.CharField(required=True, label=_('Password'))


class PasswordResponse(ResultSerializer):
    def get_data(self):
        return Password()


class EditChatUserRequestSerializer(ChatUserSerializer.UserEditInstance):
    user_group_ids = serializers.ListField(
        child=serializers.CharField(required=True),
        required=True,
        label=_('User Group IDs')
    )


class EditUserApi(APIMixin):
    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            name="user_id",
            description=_('User ID'),
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
        )]

    @staticmethod
    def get_request():
        return EditChatUserRequestSerializer


class ChatUserListResponse(serializers.Serializer):
    id = serializers.CharField(required=True, label=_('ID'))
    username = serializers.CharField(required=True, label=_('Username'))
    nick_name = serializers.CharField(required=True, label=_('Nickname'))
    email = serializers.EmailField(required=False, allow_blank=True, label=_('Email'))
    phone = serializers.CharField(required=False, allow_blank=True, label=_('Phone'))
    is_active = serializers.BooleanField(required=False, default=True, label=_('Is Active'))
    user_group_ids = serializers.ListField(
        child=serializers.CharField(required=True),
        required=True,
        label=_('User Group IDs')
    )
    user_group_names = serializers.ListField(
        child=serializers.CharField(required=True),
        required=True,
        label=_('User Group Names')
    )


class ChatUsersListResponse(ResultSerializer):
    def get_data(self):
        return ChatUserListResponse(many=True)


class ChatUserPageApi(APIMixin):
    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            name="username",
            description=_('Username'),
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
            OpenApiParameter(
                name="nick_name",
                description=_('Nickname'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name="source",
                description=_('Source'),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name="is_active",
                description=_('Is Active'),
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
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

        ]

    @staticmethod
    def get_response():
        return ChatUsersListResponse



