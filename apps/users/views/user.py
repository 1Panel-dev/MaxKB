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
from models_provider.api.model import DefaultModelResponse
from users.api.user import UserProfileAPI, TestWorkspacePermissionUserApi, DeleteUserApi, EditUserApi, \
    ChangeUserPasswordApi, UserPageApi, UserListApi
from users.serializers.user import UserProfileSerializer, UserManageSerializer


class UserProfileView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['GET'],
                   summary=_("Get current user information"),
                   description=_("Get current user information"),
                   operation_id=_("Get current user information"),  # type: ignore
                   tags=[_("User management")],  # type: ignore
                   responses=UserProfileAPI.get_response())
    def get(self, request: Request):
        return result.success(UserProfileSerializer().profile(request.user, request.auth))


class TestPermissionsUserView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['GET'],
                   summary=_("Get current user information"),
                   description=_("Get current user information"),
                   operation_id="测试",
                   tags=[_("User management")],  # type: ignore
                   responses=UserProfileAPI.get_response())
    @has_permissions(PermissionConstants.USER_EDIT)
    def get(self, request: Request):
        return result.success(UserProfileSerializer().profile(request.user, request.auth))


class TestWorkspacePermissionUserView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['GET'],
                   summary="针对工作空间下权限校验",
                   description="针对工作空间下权限校验",
                   operation_id="针对工作空间下权限校验",
                   tags=[_("User management")],  # type: ignore
                   responses=UserProfileAPI.get_response(),
                   parameters=TestWorkspacePermissionUserApi.get_parameters())
    @has_permissions(PermissionConstants.USER_EDIT.get_workspace_permission())
    def get(self, request: Request, workspace_id):
        return result.success(UserProfileSerializer().profile(request.user, request.auth))


class UserManage(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['POST'],
                   summary=_("Create user"),
                   description=_("Create user"),
                   operation_id=_("Create user"),  # type: ignore
                   tags=[_("User management")],  # type: ignore
                   request=UserProfileAPI.get_request(),
                   responses=UserProfileAPI.get_response())
    @has_permissions(PermissionConstants.USER_CREATE)
    def post(self, request: Request):
        return result.success(UserManageSerializer().save(request.data))

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['DELETE'],
                       description=_("Delete user"),
                       summary=_("Delete user"),
                       operation_id=_("Delete user"),  # type: ignore
                       tags=[_("User management")],  # type: ignore
                       parameters=DeleteUserApi.get_parameters(),
                       responses=DefaultModelResponse.get_response())
        @has_permissions(PermissionConstants.USER_DELETE)
        def delete(self, request: Request, user_id):
            return result.success(UserManageSerializer.Operate(data={'id': user_id}).delete(with_valid=True))

        @extend_schema(methods=['GET'],
                       summary=_("Get user information"),
                       description=_("Get user information"),
                       operation_id=_("Get user information"),  # type: ignore
                       tags=[_("User management")],  # type: ignore
                       request=DeleteUserApi.get_parameters(),
                       responses=UserProfileAPI.get_response())
        @has_permissions(PermissionConstants.USER_READ)
        def get(self, request: Request, user_id):
            return result.success(UserManageSerializer.Operate(data={'id': user_id}).one(with_valid=True))

        @extend_schema(methods=['PUT'],
                       summary=_("Update user information"),
                       description=_("Update user information"),
                       operation_id=_("Update user information"),  # type: ignore
                       tags=[_("User management")],  # type: ignore
                       parameters=DeleteUserApi.get_parameters(),
                       request=EditUserApi.get_request(),
                       responses=UserProfileAPI.get_response())
        @has_permissions(PermissionConstants.USER_EDIT)
        def put(self, request: Request, user_id):
            return result.success(
                UserManageSerializer.Operate(data={'id': user_id}).edit(request.data, with_valid=True))

    class RePassword(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['PUT'],
                       summary=_("Change password"),
                       description=_("Change password"),
                       operation_id=_("Change password"),  # type: ignore
                       tags=[_("User management")],  # type: ignore
                       parameters=DeleteUserApi.get_parameters(),
                       request=ChangeUserPasswordApi.get_request(),
                       responses=DefaultModelResponse.get_response())
        def put(self, request: Request, user_id):
            return result.success(
                UserManageSerializer.Operate(data={'id': user_id}).re_password(request.data, with_valid=True))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['GET'],
                       summary=_("Get user paginated list"),
                       description=_("Get user paginated list"),
                       operation_id=_("Get user paginated list"),  # type: ignore
                       tags=[_("User management")],  # type: ignore
                       parameters=UserPageApi.get_parameters(),
                       responses=UserPageApi.get_response())
        @has_permissions(PermissionConstants.USER_READ)
        def get(self, request: Request, current_page, page_size):
            d = UserManageSerializer.Query(
                data={'email_or_username': request.query_params.get('email_or_username', None),
                      'user_id': str(request.user.id)})
            return result.success(d.page(current_page, page_size))
