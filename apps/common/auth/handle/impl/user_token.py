# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： authenticate.py
    @date：2024/3/14 03:02
    @desc:  用户认证
"""
import datetime
from functools import reduce

from django.core.cache import cache
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.constants.cache_version import Cache_Version
from common.constants.permission_constants import Auth, RoleConstants, get_default_permission_list_by_role, \
    PermissionConstants
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppAuthenticationFailed
from common.utils.common import group_by
from system_manage.models.workspace_user_permission import WorkspaceUserPermission
from users.models import User


def get_permission(permission_id):
    if isinstance(permission_id, PermissionConstants):
        permission_id = permission_id.value
    return f"{permission_id}"


def get_workspace_permission(permission_id, workspace_id):
    if isinstance(permission_id, PermissionConstants):
        permission_id = permission_id.value
    return f"{permission_id}:/WORKSPACE/{workspace_id}"


def get_workspace_resource_permission_list(permission_id, workspace_id, workspace_user_permission_dict):
    workspace_user_permission_list = workspace_user_permission_dict.get(workspace_id)
    if workspace_user_permission_list is None:
        return [
            get_workspace_permission(permission_id, workspace_id), get_permission(permission_id)]
    return [
        f"{permission_id}:/WORKSPACE/{workspace_id}/{workspace_user_permission.auth_target_type}/{workspace_user_permission.taget}"
        for workspace_user_permission in
        workspace_user_permission_list if workspace_user_permission.is_auth] + [
        get_workspace_permission(permission_id, workspace_id), get_permission(permission_id)]


def get_permission_list(user,
                        workspace_user_role_mapping_model,
                        workspace_model,
                        role_model,
                        role_permission_mapping_model):
    user_id = user.id
    version = Cache_Version.PERMISSION_LIST.get_version()
    key = Cache_Version.PERMISSION_LIST.get_key(user_id=user_id)
    # 获取权限列表
    is_query_model = workspace_user_role_mapping_model is not None and workspace_model is not None and role_model is not None and role_permission_mapping_model is not None
    permission_list = cache.get(key, version=version)
    if permission_list is None:
        if is_query_model:
            # 获取工作空间 用户 角色映射数据
            workspace_user_role_mapping_list = QuerySet(workspace_user_role_mapping_model).filter(user_id=user_id)
            # 获取角色权限映射数据
            role_permission_mapping_list = QuerySet(role_permission_mapping_model).filter(
                role_id__in=[workspace_user_role_mapping.role_id for workspace_user_role_mapping in
                             workspace_user_role_mapping_list])
            role_dict = group_by(role_permission_mapping_list, lambda item: item.get('role_id'))

            workspace_user_permission_list = QuerySet(WorkspaceUserPermission).filter(
                workspace_id__in=[workspace_user_role.workspace_id for workspace_user_role in
                                  workspace_user_role_mapping_list])
            workspace_user_permission_dict = group_by(workspace_user_permission_list,
                                                      key=lambda item: item.workspace_id)
            permission_list = [
                get_workspace_resource_permission_list(role_permission_mapping.permission_id,
                                                       role_dict.get(role_permission_mapping.role_id).workspace_id,
                                                       workspace_user_permission_dict)
                for role_permission_mapping in
                role_permission_mapping_list]

            # 将二维数组扁平为一维
            permission_list = reduce(lambda x, y: [*x, *y], permission_list, [])
            cache.set(key, permission_list, version=version)
        else:
            workspace_id_list = ['default']
            workspace_user_permission_list = QuerySet(WorkspaceUserPermission).filter(
                workspace_id__in=workspace_id_list)

            workspace_user_permission_dict = group_by(workspace_user_permission_list,
                                                      key=lambda item: item.workspace_id)
            permission_list = get_default_permission_list_by_role(RoleConstants[user.role])
            permission_list = [
                get_workspace_resource_permission_list(permission, 'default', workspace_user_permission_dict) for
                permission
                in permission_list]
            # 将二维数组扁平为一维
            permission_list = reduce(lambda x, y: [*x, *y], permission_list, [])
            cache.set(key, permission_list, version=version)
    return permission_list


def get_role_list(user,
                  workspace_user_role_mapping_model,
                  workspace_model,
                  role_model,
                  role_permission_mapping_model):
    """
    获取当前用户的角色列表
    """
    version = Cache_Version.ROLE_LIST.get_version()
    key = Cache_Version.ROLE_LIST.get_key(user_id=user.id)
    workspace_list = cache.get(key, version=version)
    # 获取权限列表
    is_query_model = workspace_user_role_mapping_model is not None and workspace_model is not None and role_model is not None and role_permission_mapping_model is not None
    if workspace_list is None:
        if is_query_model:
            # 获取工作空间 用户 角色映射数据
            workspace_user_role_mapping_list = QuerySet(workspace_user_role_mapping_model).filter(user_id=user.id)
            cache.set(key,
                      [f"{workspace_user_role_mapping.role_id}:/WORKSPACE/{workspace_user_role_mapping.workspace_id}"
                       for
                       workspace_user_role_mapping in
                       workspace_user_role_mapping_list] + [user.role], version=version)
        else:
            cache.set(key, [user.role], version=version)
            return [user.role]
    return workspace_list


def get_auth(user):
    workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
    workspace_model = DatabaseModelManage.get_model("workspace_model")
    role_model = DatabaseModelManage.get_model("role_model")
    role_permission_mapping_model = DatabaseModelManage.get_model("role_permission_mapping_model")

    permission_list = get_permission_list(user, workspace_user_role_mapping_model, workspace_model,
                                          role_model, role_permission_mapping_model)
    role_list = get_role_list(user, workspace_user_role_mapping_model, workspace_model,
                              role_model, role_permission_mapping_model)
    return Auth(role_list, permission_list)


class UserToken(AuthBaseHandle):
    def support(self, request, token: str, get_token_details):
        auth_details = get_token_details()
        if auth_details is None:
            return False
        return True

    def handle(self, request, token: str, get_token_details):
        version, get_key = Cache_Version.TOKEN.value
        cache_token = cache.get(get_key(token), version=version)
        if cache_token is None:
            raise AppAuthenticationFailed(1002, _('Login expired'))
        auth_details = get_token_details()
        cache.touch(token, timeout=datetime.timedelta(seconds=60 * 60 * 2).seconds, version=version)
        user = QuerySet(User).get(id=auth_details['id'])
        auth = get_auth(user)
        return user, auth
