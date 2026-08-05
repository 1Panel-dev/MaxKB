# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： aggregate_permission.py
    @date：2026/8/5 10:11
    @desc:
"""

from typing import Protocol, List, Union

from rest_framework.request import Request

from common.auth.constants.compare_constants import CompareConstants
from common.auth.constants.permission_constants import PermissionConstants
from common.auth.constants.role_constants import RoleConstants
from common.auth.struct.permission import Role, Permission


class RoleFunc(Protocol):
    def __call__(self, request: Request, **kwargs) -> RoleConstants | Role: ...


class PermissionFunc(Protocol):
    def __call__(self, request: Request, **kwargs) -> PermissionConstants | Permission: ...


class AggregatePermission:
    def __init__(self,
                 roles: List[Union[RoleConstants, RoleFunc]] = None,
                 permissions: List[Union[PermissionConstants, PermissionFunc]] = None,
                 aggregatePermissions: List['AggregatePermission'] = None,
                 compare: CompareConstants = CompareConstants.OR):
        # 不能用可变默认值；原 stub 的 `= list` 其实是把类型对象赋进去了
        self.roles = roles if roles is not None else []
        self.permissions = permissions if permissions is not None else []
        self.aggregatePermissions = aggregatePermissions if aggregatePermissions is not None else []
        self.compare = compare

    def hasPermission(self, request: Request, **kwargs) -> bool:
        user_roles = request.auth.roles
        user_permissions = request.auth.permissions

        # 无任何约束 => 放行（对应 Java 里五个集合全空的判断）
        if not (self.roles or self.permissions or self.aggregatePermissions):
            return True

        is_and = self.compare == CompareConstants.AND

        # 惰性产出每一项的命中结果，保证 OR/AND 的短路语义
        # （return 后生成器不再前进，后面的 permission/role 不会被求值）
        def results():
            for role in self.roles:
                resolved = role(request, **kwargs) if callable(role) else role
                yield self._match_role(resolved, user_roles)
            for permission in self.permissions:
                resolved = permission(request, **kwargs) if callable(permission) else permission
                yield self._match_permission(resolved, user_permissions)
            for aggregate in self.aggregatePermissions:
                yield aggregate.hasPermission(request, **kwargs)

        for has in results():
            if has and not is_and:  # OR：命中一个即通过
                return True
            if not has and is_and:  # AND：缺一个即失败
                return False

        # AND 全部通过 => True；OR 一个都没命中 => False
        return is_and

    @staticmethod
    def _match_permission(permission: Union[PermissionConstants, Permission],
                          user_permissions: dict) -> bool:
        p = permission.value if isinstance(permission, PermissionConstants) else permission
        key = p.get_resource_permission_key(p.resource_id) if p.resource_id else str(p)
        return key in user_permissions and (user_permissions[key] & p.bit()) > 0

    @staticmethod
    def _match_role(role: Union[RoleConstants, Role], user_roles) -> bool:
        r = role.value if isinstance(role, RoleConstants) else role
        return str(r) in user_roles


ViewPermission = AggregatePermission
