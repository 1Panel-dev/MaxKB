# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： authenticate.py
    @date：2024/3/14 03:02
    @desc:  用户认证
"""
from django.core.cache import cache
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.constants.cache_version import Cache_Version
from common.constants.permission_constants import Auth, RoleConstants, get_default_permission_list_by_role
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppAuthenticationFailed
from users.models import User


def get_permission_list(user_id,
                        workspace_id,
                        workspace_user_role_mapping_model,
                        workspace_model,
                        role_model,
                        role_permission_mapping_model):
    version, get_key = Cache_Version.PERMISSION_LIST.value
    key = get_key(user_id, workspace_id)
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
            permission_list = [role_model.id for role_model in role_permission_mapping_list]
            cache.set(key, permission_list, version=version)
        else:
            permission_list = get_default_permission_list_by_role(RoleConstants.ADMIN)
            cache.set(key, permission_list, version=version)
    return permission_list


def get_workspace_list(user_id,
                       workspace_id,
                       workspace_user_role_mapping_model,
                       workspace_model,
                       role_model,
                       role_permission_mapping_model):
    version, get_key = Cache_Version.WORKSPACE_LIST.value
    key = get_key(user_id)
    workspace_list = cache.get(key, version=version)
    # 获取权限列表
    is_query_model = workspace_user_role_mapping_model is not None and workspace_model is not None and role_model is not None and role_permission_mapping_model is not None
    if workspace_list is None:
        if is_query_model:
            # 获取工作空间 用户 角色映射数据
            workspace_user_role_mapping_list = QuerySet(workspace_user_role_mapping_model).filter(user_id=user_id)
            cache.set(key, [workspace_user_role_mapping.workspace_id for workspace_user_role_mapping in
                            workspace_user_role_mapping_list], version=version)
        else:
            return ["default"]
    return workspace_list


def get_role_list(user,
                  workspace_id,
                  workspace_user_role_mapping_model,
                  workspace_model,
                  role_model,
                  role_permission_mapping_model):
    version, get_key = Cache_Version.ROLE_LIST.value
    key = get_key(user.id, workspace_id)
    workspace_list = cache.get(key, version=version)
    # 获取权限列表
    is_query_model = workspace_user_role_mapping_model is not None and workspace_model is not None and role_model is not None and role_permission_mapping_model is not None
    if workspace_list is None:
        if is_query_model:
            # 获取工作空间 用户 角色映射数据
            workspace_user_role_mapping_list = QuerySet(workspace_user_role_mapping_model).filter(user_id=user.id)
            cache.set(key, [workspace_user_role_mapping.role_id for workspace_user_role_mapping in
                            workspace_user_role_mapping_list], version=version)
        else:
            cache.set(key, [user.role], version=version)
            return [user.role]
    return workspace_list


def get_auth(user, workspace_id):
    workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
    workspace_model = DatabaseModelManage.get_model("workspace_model")
    role_model = DatabaseModelManage.get_model("role_model")
    role_permission_mapping_model = DatabaseModelManage.get_model("role_permission_mapping_model")
    workspace_list = get_workspace_list(user.id, workspace_id, workspace_user_role_mapping_model, workspace_model,
                                        role_model, role_permission_mapping_model)
    permission_list = get_permission_list(user.id, workspace_id, workspace_user_role_mapping_model, workspace_model,
                                          role_model, role_permission_mapping_model)
    role_list = get_role_list(user, workspace_id, workspace_user_role_mapping_model, workspace_model,
                              role_model, role_permission_mapping_model)
    return Auth(workspace_list, workspace_id, role_list, permission_list)


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
        # 当前工作空间
        current_workspace = auth_details['current_workspace']
        user = QuerySet(User).get(id=auth_details['id'])
        auth = get_auth(user, current_workspace)
        return user, auth
