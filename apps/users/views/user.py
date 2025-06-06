# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： user.py
    @date：2025/4/14 19:25
    @desc:
"""
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth.authenticate import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, Permission, Group, Operate
from common.log.log import log
from common.result import result
from maxkb.const import CONFIG
from models_provider.api.model import DefaultModelResponse
from tools.serializers.tool import encryption
from users.api.user import UserProfileAPI, TestWorkspacePermissionUserApi, DeleteUserApi, EditUserApi, \
    ChangeUserPasswordApi, UserPageApi, UserListApi, UserPasswordResponse, WorkspaceUserAPI
from users.models import User
from users.serializers.user import UserProfileSerializer, UserManageSerializer

default_password = CONFIG.get('default_password', 'MaxKB@123..')


def get_user_operation_object(user_id):
    user_model = QuerySet(model=User).filter(id=user_id).first()
    if user_model is not None:
        return {
            "name": user_model.name
        }
    return {}


def get_re_password_details(request):
    path = request.path
    body = request.data
    query = request.query_params
    return {
        "path": path,
        "body": {**body, 'password': encryption(body.get('password', '')),
                 're_password': encryption(body.get('re_password', ''))},
        "query": query
    }


class UserProfileView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['GET'],
                   summary=_("Get current user information"),
                   description=_("Get current user information"),
                   operation_id=_("Get current user information"),  # type: ignore
                   tags=[_("User Management")],  # type: ignore

                   responses=UserProfileAPI.get_response())
    def get(self, request: Request):
        return result.success(UserProfileSerializer().profile(request.user, request.auth))


class TestPermissionsUserView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['GET'],
                   summary=_("Get current user information"),
                   description=_("Get current user information"),
                   operation_id="测试",
                   tags=[_("User Management")],  # type: ignore
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
                   tags=[_("User Management")],  # type: ignore
                   responses=UserProfileAPI.get_response(),
                   parameters=TestWorkspacePermissionUserApi.get_parameters())
    @has_permissions(PermissionConstants.USER_EDIT.get_workspace_permission())
    def get(self, request: Request, workspace_id):
        return result.success(UserProfileSerializer().profile(request.user, request.auth))


class WorkspaceUserListView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['GET'],
                   summary=_("Get user list under workspace"),
                   description=_("Get user list under workspace"),
                   operation_id=_("Get user list under workspace"),  # type: ignore
                   tags=[_("User Management")],  # type: ignore
                   parameters=WorkspaceUserAPI.get_parameters(),
                   responses=WorkspaceUserAPI.get_response())
    def get(self, request: Request, workspace_id):
        return result.success(UserManageSerializer().get_user_list(workspace_id))


class UserManage(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['POST'],
                   summary=_("Create user"),
                   description=_("Create user"),
                   operation_id=_("Create user"),  # type: ignore
                   tags=[_("User Management")],  # type: ignore
                   request=UserProfileAPI.get_request(),
                   responses=UserProfileAPI.get_response())
    @has_permissions(PermissionConstants.USER_CREATE)
    def post(self, request: Request):
        return result.success(UserManageSerializer().save(request.data))

    class Password(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['Get'],
                       summary=_("Get default password"),
                       description=_("Get default password"),
                       operation_id=_("Get default password"),  # type: ignore
                       tags=[_("User Management")],  # type: ignore
                       responses=UserPasswordResponse.get_response())
        @has_permissions(PermissionConstants.USER_CREATE)
        def get(self, request: Request):
            return result.success(data={'password': default_password})

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['DELETE'],
                       description=_("Delete user"),
                       summary=_("Delete user"),
                       operation_id=_("Delete user"),  # type: ignore
                       tags=[_("User Management")],  # type: ignore
                       parameters=DeleteUserApi.get_parameters(),
                       responses=DefaultModelResponse.get_response())
        @has_permissions(PermissionConstants.USER_DELETE)
        @log(menu='User management', operate='Delete user',
             get_operation_object=lambda r, k: get_user_operation_object(k.get('user_id')))
        def delete(self, request: Request, user_id):
            return result.success(UserManageSerializer.Operate(data={'id': user_id}).delete(with_valid=True))

        @extend_schema(methods=['GET'],
                       summary=_("Get user information"),
                       description=_("Get user information"),
                       operation_id=_("Get user information"),  # type: ignore
                       tags=[_("User Management")],  # type: ignore
                       request=DeleteUserApi.get_parameters(),
                       responses=UserProfileAPI.get_response())
        @has_permissions(PermissionConstants.USER_READ)
        def get(self, request: Request, user_id):
            return result.success(UserManageSerializer.Operate(data={'id': user_id}).one(with_valid=True))

        @extend_schema(methods=['PUT'],
                       summary=_("Update user information"),
                       description=_("Update user information"),
                       operation_id=_("Update user information"),  # type: ignore
                       tags=[_("User Management")],  # type: ignore
                       parameters=DeleteUserApi.get_parameters(),
                       request=EditUserApi.get_request(),
                       responses=UserProfileAPI.get_response())
        @has_permissions(PermissionConstants.USER_EDIT)
        def put(self, request: Request, user_id):
            return result.success(
                UserManageSerializer.Operate(data={'id': user_id}).edit(request.data, with_valid=True))

    class BatchDelete(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['POST'],
                       description=_("Batch delete user"),
                       summary=_("Batch delete user"),
                       operation_id=_("Batch delete user"),  # type: ignore
                       tags=[_("User Management")],  # type: ignore
                       request=DeleteUserApi.get_request(),
                       responses=DefaultModelResponse.get_response())
        @has_permissions(PermissionConstants.USER_DELETE)
        @log(menu='User management', operate='Batch delete user',
             get_operation_object=lambda r, k: get_user_operation_object(k.get('user_id')))
        def post(self, request: Request):
            return result.success(UserManageSerializer.BatchDelete(data=request.data).batch_delete(with_valid=True))

    class RePassword(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['PUT'],
                       summary=_("Change password"),
                       description=_("Change password"),
                       operation_id=_("Change password"),  # type: ignore
                       tags=[_("User Management")],  # type: ignore
                       parameters=DeleteUserApi.get_parameters(),
                       request=ChangeUserPasswordApi.get_request(),
                       responses=DefaultModelResponse.get_response())
        @log(menu='User management', operate='Change password',
             get_operation_object=lambda r, k: get_user_operation_object(k.get('user_id')),
             get_details=get_re_password_details)
        def put(self, request: Request, user_id):
            return result.success(
                UserManageSerializer.Operate(data={'id': user_id}).re_password(request.data, with_valid=True))

    class Page(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['GET'],
                       summary=_("Get user paginated list"),
                       description=_("Get user paginated list"),
                       operation_id=_("Get user paginated list"),  # type: ignore
                       tags=[_("User Management")],  # type: ignore
                       parameters=UserPageApi.get_parameters(),
                       responses=UserPageApi.get_response())
        @has_permissions(PermissionConstants.USER_READ)
        def get(self, request: Request, current_page, page_size):
            d = UserManageSerializer.Query(
                data={'email_or_username': request.query_params.get('email_or_username', None),
                      'user_id': str(request.user.id)})
            return result.success(d.page(current_page, page_size))
