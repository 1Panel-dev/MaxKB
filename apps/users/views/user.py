# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： user.py
    @date：2025/4/14 19:25
    @desc:
"""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth.authenticate import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, Permission, Group, Operate
from common.result import result
from users.api.user import UserProfileAPI, TestWorkspacePermissionUserApi
from users.serializers.user import UserProfileSerializer, UserManageSerializer


class UserProfileView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['GET'],
                   description=_("Get current user information"),
                   operation_id=_("Get current user information"),
                   tags=[_("User management")],
                   responses=UserProfileAPI.get_response())
    def get(self, request: Request):
        return result.success(UserProfileSerializer().profile(request.user))


class TestPermissionsUserView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['GET'],
                   description=_("Get current user information"),
                   operation_id="测试",
                   tags=[_("User management")],
                   responses=UserProfileAPI.get_response())
    @has_permissions(PermissionConstants.USER_EDIT)
    def get(self, request: Request):
        return result.success(UserProfileSerializer().profile(request.user))


class TestWorkspacePermissionUserView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['GET'],
                   description="针对工作空间下权限校验",
                   operation_id="针对工作空间下权限校验",
                   tags=[_("User management")],
                   responses=UserProfileAPI.get_response(),
                   parameters=TestWorkspacePermissionUserApi.get_parameters())
    @has_permissions(PermissionConstants.USER_EDIT.get_workspace_permission())
    def get(self, request: Request, workspace_id):
        return result.success(UserProfileSerializer().profile(request.user))


class UserManage(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['POST'],
                   description=_("Create user"),
                   operation_id=_("Create user"),
                   tags=[_("User management")],
                   request=UserProfileAPI.get_request(),
                   responses=UserProfileAPI.get_response())
    @has_permissions(PermissionConstants.USER_CREATE)
    def post(self, request: Request):
        return result.success(UserManageSerializer().save(request.data))
