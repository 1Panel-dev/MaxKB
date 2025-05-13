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
from users.serializers.user import UserProfileResponse, CreateUserSerializer, UserManageSerializer, \
    UserInstanceSerializer
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class ApiUserProfileResponse(ResultSerializer):
    def get_data(self):
        return UserProfileResponse()


class UserProfileAPI(APIMixin):

    @staticmethod
    def get_response():
        return ApiUserProfileResponse

    @staticmethod
    def get_request():
        return CreateUserSerializer

    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            name="user_id",
            description=_('User ID'),
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
        )]


class UserPasswordResponse(APIMixin):

    @staticmethod
    def get_response():
        return PasswordResponse


class Password(serializers.Serializer):
    password = serializers.CharField(required=True, label=_('Password'))


class PasswordResponse(ResultSerializer):
    def get_data(self):
        return Password()


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
        return UserManageSerializer.UserEditInstance


class DeleteUserApi(APIMixin):
    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            name="user_id",
            description=_('User ID'),
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=True,
        )]


class ChangeUserPasswordApi(APIMixin):
    @staticmethod
    def get_request():
        return UserManageSerializer.RePasswordInstance


class UserListResponse(ResultSerializer):
    def get_data(self):
        return serializers.ListSerializer(child=UserInstanceSerializer())


class UserPageApi(APIMixin):
    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            name="email_or_username",
            description=_('Email or Username'),
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
        )]

    @staticmethod
    def get_response():
        return UserListResponse


class UserListApi(APIMixin):
    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            name="workspace_id",
            description=_('Workspace ID'),
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            required=False,
        )]

    @staticmethod
    def get_response():
        return UserListResponse


class TestWorkspacePermissionUserApi(APIMixin):
    @staticmethod
    def get_parameters():
        return [OpenApiParameter(
            # 参数的名称是done
            name="workspace_id",
            # 对参数的备注
            description="工作空间id",
            # 指定参数的类型
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            # 指定必须给
            required=True,
        )]
