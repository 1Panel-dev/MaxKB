# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： workspace_user_resource_permission.py
    @date：2025/4/28 18:13
    @desc:
"""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from system_manage.serializers.user_resource_permission import UserResourcePermissionResponse


class APIUserResourcePermissionResponse(ResultSerializer):
    def get_data(self):
        return UserResourcePermissionResponse(many=True)


class UserResourcePermissionAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description="工作空间id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ]

    @staticmethod
    def get_response():
        return APIUserResourcePermissionResponse
