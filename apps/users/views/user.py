# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： user.py
    @date：2025/4/14 19:25
    @desc:
"""
from django.core.cache import cache
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth.authenticate import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.cache_version import Cache_Version
from common.constants.permission_constants import PermissionConstants, Permission, Group, Operate, RoleConstants
from common.log.log import log
from common.result import result
from common.utils.common import query_params_to_single_dict
from maxkb.const import CONFIG
from models_provider.api.model import DefaultModelResponse
from tools.serializers.tool import encryption
from users.api.user import UserProfileAPI, TestWorkspacePermissionUserApi, DeleteUserApi, EditUserApi, \
    ChangeUserPasswordApi, UserPageApi, UserListApi, UserPasswordResponse, WorkspaceUserAPI, ResetPasswordAPI, \
    SendEmailAPI, CheckCodeAPI, SwitchUserLanguageAPI
from users.models import User
from users.serializers.user import UserProfileSerializer, UserManageSerializer, CheckCodeSerializer, \
    SendEmailSerializer, RePasswordSerializer, SwitchLanguageSerializer, ResetCurrentUserPassword

default_password = CONFIG.get('DEFAULT_PASSWORD', 'MaxKB@123..')


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
    @has_permissions(PermissionConstants.USER_EDIT, RoleConstants.ADMIN)
    def get(self, request: Request):
        return result.success(UserProfileSerializer().profile(request.user, request.auth))


class SwitchUserLanguageView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['POST'],
                   summary=_("Switch Language"),
                   description=_("Switch Language"),
                   operation_id=_("Switch Language"),  # type: ignore
                   tags=[_("User Management")],  # type: ignore
                   request=SwitchUserLanguageAPI.get_request(),
                   )
    @log(menu='User management', operate='Switch Language',
         get_operation_object=lambda r, k: {'name': r.user.username})
    @has_permissions(PermissionConstants.SWITCH_LANGUAGE, RoleConstants.ADMIN, RoleConstants.USER,
                     RoleConstants.WORKSPACE_MANAGE)
    def post(self, request: Request):
        data = {**request.data, 'user_id': request.user.id}
        return result.success(SwitchLanguageSerializer(data=data).switch())


class TestWorkspacePermissionUserView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['GET'],
                   summary="针对工作空间下权限校验",
                   description="针对工作空间下权限校验",
                   operation_id="针对工作空间下权限校验",
                   tags=[_("User Management")],  # type: ignore
                   responses=UserProfileAPI.get_response(),
                   parameters=TestWorkspacePermissionUserApi.get_parameters())
    @has_permissions(PermissionConstants.USER_EDIT.get_workspace_permission(), RoleConstants.ADMIN)
    def get(self, request: Request, workspace_id):
        return result.success(UserProfileSerializer().profile(request.user, request.auth))


class UserList(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['GET'],
                   summary=_("Get all user"),
                   description=_("Get all user"),
                   operation_id=_("Get all user"),  # type: ignore
                   tags=[_("User Management")],  # type: ignore
                   responses=UserListApi.get_response())
    def get(self, request: Request):
        return result.success(UserManageSerializer().get_all_user_list())


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


class WorkspaceUserMemberView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['GET'],
                   summary=_("Get user member under workspace"),
                   description=_("Get user member under workspace"),
                   operation_id=_("Get user member under workspace"),  # type: ignore
                   tags=[_("User Management")],  # type: ignore
                   parameters=WorkspaceUserAPI.get_parameters(),
                   responses=WorkspaceUserAPI.get_response())
    def get(self, request: Request, workspace_id):
        return result.success(UserManageSerializer().get_user_members(workspace_id))


class UserManage(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['POST'],
                   summary=_("Create user"),
                   description=_("Create user"),
                   operation_id=_("Create user"),  # type: ignore
                   tags=[_("User Management")],  # type: ignore
                   request=UserProfileAPI.get_request(),
                   responses=UserProfileAPI.get_response())
    @has_permissions(PermissionConstants.USER_CREATE, RoleConstants.ADMIN)
    @log(menu='User management', operate='Add user',
         get_operation_object=lambda r, k: {'name': r.data.get('username', None)})
    def post(self, request: Request):
        return result.success(UserManageSerializer().save(request.data, str(request.user.id)))

    class Password(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['Get'],
                       summary=_("Get default password"),
                       description=_("Get default password"),
                       operation_id=_("Get default password"),  # type: ignore
                       tags=[_("User Management")],  # type: ignore
                       responses=UserPasswordResponse.get_response())
        @has_permissions(PermissionConstants.USER_CREATE, PermissionConstants.CHAT_USER_CREATE,
                         PermissionConstants.WORKSPACE_CHAT_USER_CREATE, RoleConstants.ADMIN,
                         RoleConstants.WORKSPACE_MANAGE)
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
        @has_permissions(PermissionConstants.USER_DELETE, RoleConstants.ADMIN)
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
        @has_permissions(PermissionConstants.USER_READ, RoleConstants.ADMIN)
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
        @has_permissions(PermissionConstants.USER_EDIT, RoleConstants.ADMIN)
        @log(menu='User management', operate='Update user information',
             get_operation_object=lambda r, k: get_user_operation_object(k.get('user_id')))
        def put(self, request: Request, user_id):
            return result.success(
                UserManageSerializer.Operate(data={'id': user_id}).edit(request.data, str(request.user.id),
                                                                        with_valid=True))

    class BatchDelete(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(methods=['POST'],
                       description=_("Batch delete user"),
                       summary=_("Batch delete user"),
                       operation_id=_("Batch delete user"),  # type: ignore
                       tags=[_("User Management")],  # type: ignore
                       request=DeleteUserApi.get_request(),
                       responses=DefaultModelResponse.get_response())
        @has_permissions(PermissionConstants.USER_DELETE, RoleConstants.ADMIN)
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
        @has_permissions(PermissionConstants.USER_EDIT, RoleConstants.ADMIN)
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
        @has_permissions(PermissionConstants.USER_READ, RoleConstants.ADMIN)
        def get(self, request: Request, current_page, page_size):
            d = UserManageSerializer.Query(
                data={**query_params_to_single_dict(request.query_params)})
            return result.success(d.page(current_page, page_size, str(request.user.id)))


class RePasswordView(APIView):

    @extend_schema(methods=['POST'],
                   summary=_("Change password"),
                   description=_("Change password"),
                   operation_id=_("Change password"),  # type: ignore
                   tags=[_("User Management")],  # type: ignore
                   request=ResetPasswordAPI.get_request(),
                   responses=DefaultModelResponse.get_response())
    @log(menu='User management', operate='Change password',
         get_operation_object=lambda r, k: {'name': r.user.username},
         get_details=get_re_password_details)
    def post(self, request: Request):
        serializer_obj = RePasswordSerializer(data=request.data)
        return result.success(serializer_obj.reset_password())


class SendEmail(APIView):

    @extend_schema(methods=['POST'],
                   summary=_("Send email"),
                   description=_("Send email"),
                   operation_id=_("Send email"),  # type: ignore
                   tags=[_("User Management")],  # type: ignore
                   request=SendEmailAPI.get_request(),
                   responses=SendEmailAPI.get_response())
    @log(menu='User management', operate='Send email',
         get_operation_object=lambda r, k: {'name': r.data.get('email', None)},
         get_user=lambda r: {'user_name': None, 'email': r.data.get('email', None)})
    def post(self, request: Request):
        serializer_obj = SendEmailSerializer(data=request.data)
        if serializer_obj.is_valid(raise_exception=True):
            return result.success(serializer_obj.send())


class CheckCode(APIView):

    @extend_schema(methods=['POST'],
                   summary=_("Check whether the verification code is correct"),
                   description=_("Check whether the verification code is correct"),
                   operation_id=_("Check whether the verification code is correct"),  # type: ignore
                   tags=[_("User Management")],  # type: ignore
                   request=CheckCodeAPI.get_request(),
                   responses=CheckCodeAPI.get_response())
    @log(menu='User management', operate='Check whether the verification code is correct',
         get_operation_object=lambda r, k: {'name': r.data.get('email', None)},
         get_user=lambda r: {'user_name': None, 'email': r.data.get('email', None)})
    def post(self, request: Request):
        return result.success(CheckCodeSerializer(data=request.data).is_valid(raise_exception=True))


class SendEmailToCurrentUserView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['POST'],
                   summary=_("Send email to current user"),
                   description=_("Send email to current user"),
                   operation_id=_("Send email to current user"),  # type: ignore
                   tags=[_("User Management")],  # type: ignore
                   request=SendEmailAPI.get_request(),
                   responses=SendEmailAPI.get_response())
    @log(menu='User management', operate='Send email to current user',
         get_operation_object=lambda r, k: {'name': r.user.username})
    def post(self, request: Request):
        serializer_obj = SendEmailSerializer(data={'email': request.user.email, 'type': "reset_password"})
        if serializer_obj.is_valid(raise_exception=True):
            return result.success(serializer_obj.send())


class ResetCurrentUserPasswordView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['POST'],
                   summary=_("Modify current user password"),
                   description=_("Modify current user password"),
                   operation_id=_("Modify current user password"),  # type: ignore
                   tags=[_("User Management")],  # type: ignore
                   request=ResetPasswordAPI.get_request(),
                   responses=DefaultModelResponse.get_response())
    @log(menu='User management', operate='Modify current user password',
         get_operation_object=lambda r, k: {'name': r.user.username},
         get_details=get_re_password_details)
    @has_permissions(PermissionConstants.CHANGE_PASSWORD, RoleConstants.ADMIN, RoleConstants.USER,
                     RoleConstants.WORKSPACE_MANAGE)
    def post(self, request: Request):
        serializer_obj = ResetCurrentUserPassword(data=request.data)
        if serializer_obj.reset_password(request.user.id):
            version, get_key = Cache_Version.TOKEN.value
            cache.delete(get_key(token=request.auth), version=version)
            return result.success(True)
        return result.error(_("Failed to change password"))
