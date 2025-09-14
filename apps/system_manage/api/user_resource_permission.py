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
from common.result import ResultSerializer, ResultPageSerializer, PageDataResponse
from system_manage.serializers.user_resource_permission import ResourceUserPermissionEditRequest, UpdateTeamMemberItemPermissionSerializer


class UserResourcePermissionResponse0(serializers.Serializer):
    id = serializers.UUIDField(required=True, label="主键id")
    name = serializers.CharField(required=True, label="资源名称")
    auth_target_type = serializers.CharField(required=True, label="授权资源")
    user_id = serializers.UUIDField(required=True, label="用户id")
    icon = serializers.CharField(required=True, label="资源图标")
    auth_type = serializers.CharField(required=True, label="授权类型")
    permission = serializers.ChoiceField(required=False, allow_null=True, allow_blank=True,
                                         choices=['NOT_AUTH', 'MANAGE', 'VIEW', 'ROLE'],
                                         label=_('permission'))

class NewAPIUserResourcePermissionResponse(ResultSerializer):
    def get_data(self):
        return UserResourcePermissionResponse0(many=True)

class NewAPIUserResourcePermissionPageResponse(ResultPageSerializer):

    def get_data(self):
        return UserResourcePermissionResponse0(many=True)

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
            OpenApiParameter(
                name="name",
                description="名称",
                type=OpenApiTypes.STR,
                location='query',
                required=False
            ),
            OpenApiParameter(
                name="permission",
                description="权限",
                type=OpenApiTypes.STR,
                location='query',
                many=True,
                required=False
            ),
        ]

    @staticmethod
    def get_response():
        return NewAPIUserResourcePermissionResponse


class EditUserResourcePermissionAPI(APIMixin):
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
            OpenApiParameter(
                name="resource",
                description="资源类型",
                type=OpenApiTypes.STR,
                location='path',
                required=True
            ),
        ]

    @staticmethod
    def get_request():
        return UpdateTeamMemberItemPermissionSerializer(many=True)

    @staticmethod
    def get_response():
        return NewAPIUserResourcePermissionResponse


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
            OpenApiParameter(
                name="permission",
                description="权限",
                type=OpenApiTypes.STR,
                location='query',
                many=True,
                required=False
            ),
        ]

    @staticmethod
    def get_response():
        return APIResourceUserPermissionResponse

class UserResourcePermissionPageAPI(APIMixin):
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
                name="user_id",
                description="用户id",
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
                name="name",
                description="资源名称",
                type=OpenApiTypes.STR,
                location='query',
                required=False
            ),
            OpenApiParameter(
                name="permission[]",
                description="权限",
                type=OpenApiTypes.STR,
                location='query',
                many=True,
                required=False
            ),
        ]

    @staticmethod
    def get_response():
        return NewAPIUserResourcePermissionPageResponse


class APIResourceUserPermissionPageResponse(ResultPageSerializer):
    def get_data(self):
        return PageDataResponse(ResourceUserPermissionResponse(many=True))


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
            OpenApiParameter(
                name="permission[]",
                description="权限",
                type=OpenApiTypes.STR,
                location='query',
                many=True,
                required=False
            ),
        ]

    @staticmethod
    def get_response():
        return APIResourceUserPermissionPageResponse



class ResourceUserPermissionEditAPI(APIMixin):
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
        ]
    @staticmethod
    def get_request():
        return ResourceUserPermissionEditRequest(required=True, many=True, label=_('users_permission'))

    @staticmethod
    def get_response():
        return APIResourceUserPermissionResponse()