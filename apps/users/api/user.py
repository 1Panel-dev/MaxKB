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
from users.serializers.user import UserProfileResponse, CreateUserSerializer


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
