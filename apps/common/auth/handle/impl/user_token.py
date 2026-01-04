# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： authenticate.py
    @date：2024/3/14 03:02
    @desc:  用户认证
"""
from functools import reduce
from typing import List

from django.core.cache import cache
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.constants.authentication_type import AuthenticationType
from common.constants.cache_version import Cache_Version
from common.constants.permission_constants import Auth, PermissionConstants, ResourcePermissionGroup, \
    get_permission_list_by_resource_group, ResourceAuthType, \
    ResourcePermissionRole, get_default_role_permission_mapping_list, get_default_workspace_user_role_mapping_list, \
    RoleConstants, ResourcePermission, Resource, WorkspaceGroup
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppAuthenticationFailed
from common.utils.common import group_by
from maxkb.const import CONFIG
from system_manage.models.workspace_user_permission import WorkspaceUserResourcePermission
from users.models import User

permission_constants_dict = {p.value.__str__(): p for p in PermissionConstants}

def get_permission(permission_id):
    """
    获取权限字符串
    @param permission_id: 权限id
    @return:  权限字符串
    """
    if isinstance(permission_id, PermissionConstants):
        permission_id = permission_id.value
    return f"{permission_id}"


def get_workspace_permission(permission_id, workspace_id, role=None):
    """
    获取工作空间权限字符串
    @param permission_id: 权限id
    @param workspace_id:  工作空间id
    @param role:     角色
    @return:
    """
    if isinstance(permission_id, PermissionConstants):
        permission_id = permission_id.value
    if role and role.type == RoleConstants.WORKSPACE_MANAGE.value.__str__():
        return [f"{permission_id}:/WORKSPACE/{workspace_id}:ROLE/{role.type}",
                f"{permission_id}:/WORKSPACE/{workspace_id}"]
    return [f"{permission_id}:/WORKSPACE/{workspace_id}"]


def get_role_permission(role, workspace_id):
    """
    获取工作空间角色
    @param role:  角色
    @param workspace_id: 工作空间id
    @return:
    """
    if isinstance(role, RoleConstants):
        role = role.value
    return f"{role}:/WORKSPACE/{workspace_id}"


def get_workspace_permission_list(role_permission_mapping_dict, workspace_user_role_mapping_list, role_model_dict):
    """
    获取工作空间下所有的权限
    @param role_permission_mapping_dict:   角色权限关联字典
    @param workspace_user_role_mapping_list: 工作空间用户角色关联列表
    @param role_model_dict:         角色字典
    @return: 工作空间下的权限
    """
    workspace_permission_list = [
        [get_workspace_permission(role_permission_mapping.permission_id, w_u_r.workspace_id,
                                  role_model_dict.get(w_u_r.role_id, None)) for role_permission_mapping
         in
         role_permission_mapping_dict.get(w_u_r.role_id, [])] for w_u_r in workspace_user_role_mapping_list]
    return reduce(lambda x, y: [*x, *y], reduce(lambda x, y: [*x, *y], workspace_permission_list, []), [])


def get_workspace_resource_permission_list(
        workspace_user_resource_permission_list: List[WorkspaceUserResourcePermission],
        role_permission_mapping_dict,
        workspace_user_role_mapping_dict):
    """

    @param workspace_user_resource_permission_list: 工作空间用户资源权限列表
    @param role_permission_mapping_dict:            角色权限关联字典        key为role_id
    @param workspace_user_role_mapping_dict:        工作空间用户角色映射字典  key为role_id
    @return: 工作空间资源权限列表
    """
    resource_permission_list = [
        get_workspace_resource_permission_list_by_workspace_user_permission(workspace_user_resource_permission,
                                                                            role_permission_mapping_dict,
                                                                            workspace_user_role_mapping_dict) for
        workspace_user_resource_permission in workspace_user_resource_permission_list]
    # 将二维数组扁平为一维
    return reduce(lambda x, y: [*x, *y], resource_permission_list, [])


def get_workspace_resource_permission_list_by_workspace_user_permission(
        workspace_user_resource_permission: WorkspaceUserResourcePermission,
        role_permission_mapping_dict,
        workspace_user_role_mapping_dict):
    """

    @param workspace_user_resource_permission: 工作空间用户资源权限对象
    @param role_permission_mapping_dict:       角色权限关联字典            key为role_id
    @param workspace_user_role_mapping_dict:   工作空间用户角色关联字典  key为role_id
    @return: 工作空间用户资源的权限列表
    """
    role_permission_mapping_list = [role_permission_mapping_dict.get(workspace_user_role_mapping.role_id, []) for
                                    workspace_user_role_mapping in
                                    workspace_user_role_mapping_dict.get(
                                        workspace_user_resource_permission.workspace_id)]
    role_permission_mapping_list = reduce(lambda x, y: [*x, *y], role_permission_mapping_list, [])
    # 如果是根据角色
    if (workspace_user_resource_permission.auth_type == ResourceAuthType.ROLE
            and workspace_user_resource_permission.permission_list.__contains__(
                ResourcePermissionRole.ROLE)):
        return [
            f"{role_permission_mapping.permission_id}:/WORKSPACE/{workspace_user_resource_permission.workspace_id}/{workspace_user_resource_permission.auth_target_type}/{workspace_user_resource_permission.target}"
            for role_permission_mapping in role_permission_mapping_list if (permission_constants_dict.get(role_permission_mapping.permission_id).value.parent_group or []).__contains__(
                                        WorkspaceGroup(workspace_user_resource_permission.auth_target_type))] + [
            f"{workspace_user_resource_permission.auth_target_type}:/WORKSPACE/{workspace_user_resource_permission.workspace_id}/{workspace_user_resource_permission.auth_target_type}/{workspace_user_resource_permission.target}"]

    elif workspace_user_resource_permission.auth_type == ResourceAuthType.RESOURCE_PERMISSION_GROUP:
        resource_permission_list = [
            [
                f"{permission}:/WORKSPACE/{workspace_user_resource_permission.workspace_id}/{workspace_user_resource_permission.auth_target_type}/{workspace_user_resource_permission.target}"
                for permission in get_permission_list_by_resource_group(
                ResourcePermissionGroup(Resource(workspace_user_resource_permission.auth_target_type),
                                        ResourcePermission(resource_permission)))]
            for resource_permission in workspace_user_resource_permission.permission_list if
            ResourcePermission.values.__contains__(resource_permission)]
        # 将二维数组扁平为一维
        return reduce(lambda x, y: [*x, *y], resource_permission_list, [])
    return []


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
            workspace_user_role_mapping_dict = group_by(workspace_user_role_mapping_list,
                                                        lambda item: item.workspace_id)
            role_id_list = list(set([workspace_user_role_mapping.role_id for workspace_user_role_mapping in
                                     workspace_user_role_mapping_list]))
            # 获取角色权限映射数据
            role_permission_mapping_list = QuerySet(role_permission_mapping_model).filter(
                role_id__in=role_id_list)
            role_model_list = QuerySet(role_model).filter(id__in=role_id_list)

            role_model_dict = {role_model.id: role_model for role_model in role_model_list}

            role_permission_mapping_dict = group_by(
                role_permission_mapping_list, lambda item: item.role_id)

            workspace_user_permission_list = QuerySet(WorkspaceUserResourcePermission).filter(
                workspace_id__in=[workspace_user_role.workspace_id for workspace_user_role in
                                  workspace_user_role_mapping_list if
                                  (role_model_dict.get(workspace_user_role.role_id).type == 'USER' if
                                   role_model_dict.get(workspace_user_role.role_id) else False)],
                user_id=user_id)

            # 资源权限
            workspace_resource_permission_list = get_workspace_resource_permission_list(workspace_user_permission_list,
                                                                                        role_permission_mapping_dict,
                                                                                        workspace_user_role_mapping_dict)

            workspace_permission_list = get_workspace_permission_list(role_permission_mapping_dict,
                                                                      workspace_user_role_mapping_list, role_model_dict)
            # 系统权限
            system_permission_list = [role_permission_mapping.permission_id for role_permission_mapping in
                                      role_permission_mapping_list]
            # 合并权限
            permission_list = system_permission_list + workspace_permission_list + workspace_resource_permission_list
            permission_list = list(set(permission_list))
            cache.set(key, permission_list, version=version)
        else:
            workspace_id_list = ['default']
            workspace_user_resource_permission_list = QuerySet(WorkspaceUserResourcePermission).filter(
                workspace_id__in=workspace_id_list, user_id=user_id)
            role_permission_mapping_list = get_default_role_permission_mapping_list()
            role_permission_mapping_dict = group_by(role_permission_mapping_list, lambda item: item.role_id)
            workspace_user_role_mapping_list = get_default_workspace_user_role_mapping_list([user.role])
            workspace_user_role_mapping_dict = group_by(workspace_user_role_mapping_list,
                                                        lambda item: item.workspace_id)
            # 资源权限
            workspace_resource_permission_list = get_workspace_resource_permission_list(
                workspace_user_resource_permission_list,
                role_permission_mapping_dict,
                workspace_user_role_mapping_dict)
            # 合并权限
            permission_list = workspace_resource_permission_list
            permission_list = list(set(permission_list))
            cache.set(key, permission_list, version=version)
    return permission_list


system_role_list = [RoleConstants.ADMIN.value.name, RoleConstants.WORKSPACE_MANAGE.value.name,
                    RoleConstants.USER.value.name]

system_role = RoleConstants.ADMIN.value.name


def reset_workspace_role(role_id, workspace_id, role_dict):
    if system_role_list.__contains__(role_id):
        if system_role == role_id:
            return [role_id]
        else:
            return [f"{role_id}:/WORKSPACE/{workspace_id}", role_id]
    else:
        r = role_dict.get(role_id)
        if r is None:
            return ''
        role_type = role_dict.get(role_id).type
        if system_role == role_type:
            return [RoleConstants.EXTENDS_ADMIN.value.name]
        return [f"EXTENDS_{role_type}:/WORKSPACE/{workspace_id}", f"EXTENDS_{role_type}"]


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
            role_list = QuerySet(role_model).filter(id__in=[wurm.role_id for wurm in workspace_user_role_mapping_list])
            role_dict = {r.id: r for r in role_list}
            role_list = list(
                set(reduce(lambda x, y: [*x, *y], [reset_workspace_role(workspace_user_role_mapping.role_id,
                                                                        workspace_user_role_mapping.workspace_id,
                                                                        role_dict)
                                                   for
                                                   workspace_user_role_mapping in
                                                   workspace_user_role_mapping_list], [])))
            cache.set(key, workspace_list, version=version)
            return role_list
        else:
            if user.role == RoleConstants.ADMIN.value.__str__():
                role_list = [user.role, get_role_permission(RoleConstants.WORKSPACE_MANAGE, 'default')]
            else:
                role_list = [user.role, get_role_permission(RoleConstants.USER, 'default')]
            cache.set(key, role_list, version=version)
            return role_list
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
        return 'id' in auth_details and auth_details.get('type') == AuthenticationType.SYSTEM_USER.value

    def handle(self, request, token: str, get_token_details):
        version, get_key = Cache_Version.TOKEN.value
        cache_token = cache.get(get_key(token), version=version)
        if cache_token is None:
            raise AppAuthenticationFailed(1002, _('Login expired'))
        auth_details = get_token_details()
        timeout = CONFIG.get_session_timeout()
        cache.touch(token, timeout=timeout, version=version)
        user = QuerySet(User).get(id=auth_details['id'])
        if not user.is_active or user.password != cache_token.password:
            raise AppAuthenticationFailed(1002, _('Authentication information is incorrect'))
        auth = get_auth(user)
        return user, auth
