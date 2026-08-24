# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： authenticate.py
@date：2024/3/14 03:02
@desc:  用户认证
"""

from functools import reduce

from django.core.cache import cache
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from common.auth.constants.permission_constants import RESOURCE_PERMISSION_MAP, PERMISSION_STR_MAP
from common.auth.constants.permission_scope_constants import PermissionScopeConstants
from common.constants.resource_permission_constants import ResourceAuthType
from common.auth.constants.role_constants import RoleConstants
from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.auth.struct.auth import Auth, Principal
from common.constants.authentication_type import AuthenticationType, UserType
from common.constants.cache_version import Cache_Version

from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import AppAuthenticationFailed
from common.utils.common import group_by, flat_map
from maxkb.const import CONFIG
from system_manage.models.workspace_user_group_permission import WorkspaceUserGroupResourcePermission
from system_manage.models.workspace_user_permission import WorkspaceUserResourcePermission
from users.models import User


def get_permissions(
    user, workspace_user_role_mapping_model, workspace_model, role_model, role_permission_mapping_model
):
    user_id = user.id
    version = Cache_Version.PERMISSION_LIST.get_version()
    key = Cache_Version.PERMISSION_LIST.get_key(user_id=user_id)
    # 获取权限列表
    is_query_model = (
        workspace_user_role_mapping_model is not None
        and workspace_model is not None
        and role_model is not None
        and role_permission_mapping_model is not None
    )
    permission_map = cache.get(key, version=version)
    if permission_map is None:
        permission_map = {}
        if is_query_model:
            # 获取工作空间 用户 角色映射数据
            workspace_user_role_mapping_list = QuerySet(workspace_user_role_mapping_model).filter(user_id=user_id)

            role_id_list = list(
                set(
                    [
                        workspace_user_role_mapping.role_id
                        for workspace_user_role_mapping in workspace_user_role_mapping_list
                    ]
                )
            )
            # 获取角色权限映射数据
            role_permission_mapping_list = QuerySet(role_permission_mapping_model).filter(role_id__in=role_id_list)
            role_model_list = QuerySet(role_model).filter(id__in=role_id_list)

            role_model_dict = {role_model.id: role_model for role_model in role_model_list}

            role_permission_mapping_dict = group_by(role_permission_mapping_list, lambda item: str(item.role_id))

            workspace_user_permission_list = QuerySet(WorkspaceUserResourcePermission).filter(
                workspace_id__in=[
                    workspace_user_role.workspace_id
                    for workspace_user_role in workspace_user_role_mapping_list
                    if (
                        role_model_dict.get(workspace_user_role.role_id).type == "USER"
                        if role_model_dict.get(workspace_user_role.role_id)
                        else False
                    )
                ],
                user_id=user_id,
            )

            workspace_user_group_resource_permission_list = (
                QuerySet(WorkspaceUserGroupResourcePermission)
                .filter(user_group__user_relations__user_id=user_id)
                .select_related("user_group")
                .distinct()
            )
            "----------------------处理资源权限--------------------------------------------------"
            for _ in list(workspace_user_permission_list) + list(workspace_user_group_resource_permission_list):
                if _.auth_type == ResourceAuthType.RESOURCE_PERMISSION_GROUP:
                    all_permissions = flat_map(
                        [
                            RESOURCE_PERMISSION_MAP.get(f"{_.auth_target_type}_{_resource_permission}")
                            for _resource_permission in _.permission_list
                            if _resource_permission in ["VIEW", "MANAGE"]
                        ]
                    )
                    for group, permissions in group_by(
                        all_permissions, lambda _permission: _permission.value.group
                    ).items():
                        k = f"{group}:{_.workspace_id}:{_.target}"
                        bits = reduce(lambda x, y: x | y, [_permission.value.bit() for _permission in permissions], 0)
                        permission_map[k] = permission_map.get(k, 0) | bits
                elif _.auth_type == ResourceAuthType.ROLE:
                    role_ids = [m.role_id for m in workspace_user_role_mapping_list if m.workspace_id == _.workspace_id]

                    permissions = []
                    for role_id in role_ids:
                        for m in role_permission_mapping_dict.get(str(role_id)) or []:
                            p = PERMISSION_STR_MAP.get(m.permission_id)
                            if PermissionScopeConstants.WORKSPACE in p.meta.scope:
                                permissions.append(p)

                    for group, ps in group_by(permissions, lambda p: p.meta.group).items():
                        k = f"{group}:w:{_.workspace_id}:r:{_.target}"
                        bits = reduce(lambda x, y: x | y, [p.value.bit() for p in ps], 0)
                        permission_map[k] = permission_map.get(k, 0) | bits

            "----------------------处理工作空间权限--------------------------------------------------"
            for _ in workspace_user_role_mapping_list:
                _role_permission_mapping_list = role_permission_mapping_dict.get(str(_.role_id)) or []
                permissions = [
                    PERMISSION_STR_MAP.get(_role_permission_mapping.permission_id)
                    for _role_permission_mapping in _role_permission_mapping_list
                ]
                # 过滤工作空间权限
                permissions = [
                    _permission
                    for _permission in permissions
                    if PermissionScopeConstants.WORKSPACE in _permission.meta.scope
                ]
                for group, ps in group_by(permissions, lambda p: p.meta.group).items():
                    k = f"{group}:w:{_.workspace_id}"
                    bits = reduce(lambda x, y: x | y, [p.value.bit() for p in ps], 0)
                    permission_map[k] = permission_map.get(k, 0) | bits
            "----------------------处理系统权限--------------------------------------------------"
            system_permissions = [
                PERMISSION_STR_MAP.get(_role_permission_mapping.permission_id)
                for _role_permission_mapping in role_permission_mapping_list
            ]
            system_permissions = [
                _permission
                for _permission in system_permissions
                if PermissionScopeConstants.SYSTEM in _permission.meta.scope
            ]
            for group, permissions in group_by(system_permissions, lambda _permission: _permission.meta.group).items():
                permission_map[f"{group}"] = reduce(
                    lambda x, y: x | y, [_permission.value.bit() for _permission in permissions], 0
                )
            cache.set(key, permission_map, version=version)
        else:
            workspace_id_list = ["default"]
            workspace_user_permission_list = QuerySet(WorkspaceUserResourcePermission).filter(
                workspace_id__in=workspace_id_list, user_id=user_id
            )
            workspace_user_group_resource_permission_list = (
                QuerySet(WorkspaceUserGroupResourcePermission)
                .filter(user_group__user_relations__user_id=user_id)
                .select_related("user_group")
                .distinct()
            )

            for _ in list(workspace_user_permission_list) + list(workspace_user_group_resource_permission_list):
                if _.auth_type == ResourceAuthType.RESOURCE_PERMISSION_GROUP:
                    all_permissions = flat_map(
                        [
                            RESOURCE_PERMISSION_MAP.get(f"{_.auth_target_type}_{_resource_permission}")
                            for _resource_permission in _.permission_list
                            if _resource_permission in ["VIEW", "MANAGE"]
                        ]
                    )
                    for group, permissions in group_by(
                        all_permissions, lambda _permission: _permission.value.group
                    ).items():
                        permission_map[f"{group}:w:{_.workspace_id}:r:{_.target}"] = reduce(
                            lambda x, y: x | y, [_permission.value.bit() for _permission in permissions], 0
                        )
            cache.set(key, permission_map, version=version)

    return permission_map


system_role_list = [
    RoleConstants.ADMIN.value.name,
    RoleConstants.WORKSPACE_MANAGE.value.name,
    RoleConstants.USER.value.name,
]

system_role = RoleConstants.ADMIN.value.name


def reset_workspace_role(role_id, workspace_id, role_dict):
    if system_role_list.__contains__(role_id):
        if system_role == role_id:
            return [role_id]
        else:
            return [f"{role_id}:w:{workspace_id}", role_id]
    else:
        r = role_dict.get(role_id)
        if r is None:
            return []
        role_type = role_dict.get(role_id).type
        if system_role == role_type:
            return [RoleConstants.EXTENDS_ADMIN.value.name]
        return [f"EXTENDS_{role_type}:w:{workspace_id}"]


def get_role_list(user, workspace_user_role_mapping_model, workspace_model, role_model, role_permission_mapping_model):
    """
    获取当前用户的角色列表
    """
    version = Cache_Version.ROLE_LIST.get_version()
    key = Cache_Version.ROLE_LIST.get_key(user_id=user.id)
    role_list = cache.get(key, version=version)
    # 获取权限列表
    is_query_model = (
        workspace_user_role_mapping_model is not None
        and workspace_model is not None
        and role_model is not None
        and role_permission_mapping_model is not None
    )
    if role_list is None:
        if is_query_model:
            # 获取工作空间 用户 角色映射数据
            workspace_user_role_mapping_list = QuerySet(workspace_user_role_mapping_model).filter(user_id=user.id)
            role_list = QuerySet(role_model).filter(id__in=[wurm.role_id for wurm in workspace_user_role_mapping_list])
            role_dict = {r.id: r for r in role_list}
            role_list = list(
                set(
                    reduce(
                        lambda x, y: [*x, *y],
                        [
                            reset_workspace_role(
                                workspace_user_role_mapping.role_id, workspace_user_role_mapping.workspace_id, role_dict
                            )
                            for workspace_user_role_mapping in workspace_user_role_mapping_list
                        ],
                        [],
                    )
                )
            )
            cache.set(key, role_list, version=version)
        else:
            if user.role == RoleConstants.ADMIN.value.__str__():
                role_list = [user.role, f"{RoleConstants.WORKSPACE_MANAGE}:w:default"]
            else:
                role_list = [user.role, f"{RoleConstants.USER}:w:default"]
            cache.set(key, role_list, version=version)
    return role_list


def get_auth(user):
    workspace_user_role_mapping_model = DatabaseModelManage.get_model("workspace_user_role_mapping")
    workspace_model = DatabaseModelManage.get_model("workspace_model")
    role_model = DatabaseModelManage.get_model("role_model")
    role_permission_mapping_model = DatabaseModelManage.get_model("role_permission_mapping_model")

    permissions = get_permissions(
        user, workspace_user_role_mapping_model, workspace_model, role_model, role_permission_mapping_model
    )
    role_list = get_role_list(
        user, workspace_user_role_mapping_model, workspace_model, role_model, role_permission_mapping_model
    )
    return Auth(set(role_list), permissions)


class UserToken(AuthBaseHandle):
    def support(self, request, token: str, get_token_details):
        auth_details = get_token_details()
        if auth_details is None:
            return False
        return "id" in auth_details and auth_details.get("type") == AuthenticationType.SYSTEM_USER.value

    def handle(self, request, token: str, get_token_details):
        version, get_key = Cache_Version.TOKEN.value
        cache_token = cache.get(get_key(token), version=version)
        if cache_token is None:
            raise AppAuthenticationFailed(1002, _("Login expired"))
        auth_details = get_token_details()
        timeout = CONFIG.get_session_timeout()
        cache.touch(token, timeout=timeout, version=version)
        user = QuerySet(User).get(id=auth_details["id"])
        if not user.is_active or user.password != cache_token.password:
            raise AppAuthenticationFailed(1002, _("Authentication information is incorrect"))
        auth = get_auth(user)
        return Principal(user.id, UserType.SYSTEM_USER, user), auth
