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
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer, ResultPageSerializer
from system_manage.serializers.user_resource_permission import UserResourcePermissionResponse, \
    UpdateUserResourcePermissionRequest


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
            ),
            OpenApiParameter(
                name="user_id",
                description="用户id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return APIUserResourcePermissionResponse


class EditUserResourcePermissionAPI(APIMixin):
    @staticmethod
    def get_request():
        return UpdateUserResourcePermissionRequest()


class ResourceUserPermissionResponse(serializers.Serializer):
    id = serializers.CharField(required=True, label=_('user id'))
    nick_name = serializers.CharField(required=True, allow_null=True, allow_blank=True, label=_('nick_name'))
    username = serializers.CharField(required=True, allow_null=True, allow_blank=True, label=_('username'))
    permission = serializers.CharField(required=True, label=_('permission'))


class APIResourceUserPermissionResponse(ResultSerializer):
    def get_data(self):
        return ResourceUserPermissionResponse(many=True)


class ResourceUserPermissionAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description="工作空间id",
                type=OpenApiTypes.STR,
                location='path',
                required=True
            ),
            OpenApiParameter(
                name="target",
                description="资源id",
                type=OpenApiTypes.STR,
                location='path',
                required=True
            ),
            OpenApiParameter(
                name="resource",
                description="资源类型",
                type=OpenApiTypes.STR,
                location='path',
                required=True
            ),
            OpenApiParameter(
                name="username",
                description="用户名",
                type=OpenApiTypes.STR,
                location='query',
                required=False
            ),
            OpenApiParameter(
                name="nick_name",
                description="姓名",
                type=OpenApiTypes.STR,
                location='query',
                required=False
            ),
        ]

    @staticmethod
    def get_response():
        return APIResourceUserPermissionResponse


class APIResourceUserPermissionPageResponse(ResultPageSerializer):
    def get_data(self):
        return ResourceUserPermissionResponse(many=True)


class ResourceUserPermissionPageAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description="工作空间id",
                type=OpenApiTypes.STR,
                location='path',
                required=True
            ),
            OpenApiParameter(
                name="target",
                description="资源id",
                type=OpenApiTypes.STR,
                location='path',
                required=True
            ),
            OpenApiParameter(
                name="resource",
                description="资源类型",
                type=OpenApiTypes.STR,
                location='path',
                required=True
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
                name="username",
                description="用户名",
                type=OpenApiTypes.STR,
                location='query',
                required=False
            ),
            OpenApiParameter(
                name="nick_name",
                description="姓名",
                type=OpenApiTypes.STR,
                location='query',
                required=False
            ),
        ]

    @staticmethod
    def get_response():
        return APIResourceUserPermissionPageResponse
