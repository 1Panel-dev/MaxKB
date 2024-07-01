# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： authentication.py
    @date：2023/9/13 15:00
    @desc: 鉴权
"""
from typing import List

from common.constants.permission_constants import ViewPermission, CompareConstants, RoleConstants, PermissionConstants, \
    Permission
from common.exception.app_exception import AppUnauthorizedFailed


def exist_permissions_by_permission_constants(user_permission: List[PermissionConstants],
                                              permission_list: List[PermissionConstants]):
    """
    用户是否拥有 permission_list的权限
    :param user_permission:  用户权限
    :param permission_list:  需要的权限
    :return: 是否拥有
    """
    return any(list(map(lambda up: permission_list.__contains__(up), user_permission)))


def exist_role_by_role_constants(user_role: List[RoleConstants],
                                 role_list: List[RoleConstants]):
    """
    用户是否拥有这个角色
    :param user_role: 用户角色
    :param role_list: 需要拥有的角色
    :return:  是否拥有
    """
    return any(list(map(lambda up: role_list.__contains__(up), user_role)))


def exist_permissions_by_view_permission(user_role: List[RoleConstants],
                                         user_permission: List[PermissionConstants | object],
                                         permission: ViewPermission, request, **kwargs):
    """
    用户是否存在这些权限
    :param request:
    :param user_role:        用户角色
    :param user_permission:  用户权限
    :param permission:       所属权限
    :return:                 是否存在 True False
    """
    role_ok = any(list(map(lambda ur: permission.roleList.__contains__(ur), user_role)))
    permission_list = [user_p(request, kwargs) if callable(user_p) else user_p for user_p in
                       permission.permissionList
                       ]
    permission_ok = any(list(map(lambda up: permission_list.__contains__(up),
                                 user_permission)))
    return role_ok | permission_ok if permission.compare == CompareConstants.OR else role_ok & permission_ok


def exist_permissions(user_role: List[RoleConstants], user_permission: List[PermissionConstants], permission, request,
                      **kwargs):
    if isinstance(permission, ViewPermission):
        return exist_permissions_by_view_permission(user_role, user_permission, permission, request, **kwargs)
    if isinstance(permission, RoleConstants):
        return exist_role_by_role_constants(user_role, [permission])
    if isinstance(permission, PermissionConstants):
        return exist_permissions_by_permission_constants(user_permission, [permission])
    if isinstance(permission, Permission):
        return user_permission.__contains__(permission)
    return False


def exist(user_role: List[RoleConstants], user_permission: List[PermissionConstants], permission, request, **kwargs):
    if callable(permission):
        p = permission(request, kwargs)
        return exist_permissions(user_role, user_permission, p, request)
    return exist_permissions(user_role, user_permission, permission, request, **kwargs)


def has_permissions(*permission, compare=CompareConstants.OR):
    """
    权限 role or permission
    :param compare:    比较符号
    :param permission: 如果是角色 role:roleId
    :return: 权限装饰器函数,用于判断用户是否有权限访问当前接口
    """

    def inner(func):
        def run(view, request, **kwargs):
            exit_list = list(
                map(lambda p: exist(request.auth.role_list, request.auth.permission_list, p, request, **kwargs),
                    permission))
            # 判断是否有权限
            if any(exit_list) if compare == CompareConstants.OR else all(exit_list):
                return func(view, request, **kwargs)
            raise AppUnauthorizedFailed(403, "没有权限访问")

        return run

    return inner
