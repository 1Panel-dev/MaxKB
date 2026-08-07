# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： permission.py
    @date：2026/8/3 17:29
    @desc:
"""
from dataclasses import dataclass, field
from typing import Optional

from common.auth.constants.category_constants import Category
from common.auth.constants.group_constants import Group
from common.auth.constants.operate_constants import Operate
from common.auth.constants.permission_scope_constants import PermissionScopeConstants
from common.auth.constants.role_group import RoleGroup


@dataclass(frozen=True)
class Permission:
    """
    权限信息
    """
    group: Group | str
    sub_group: Group | str
    operate: Operate
    bit_index: int
    workspace_id: Optional[str] = None
    resource_id: Optional[str] = None
    flag: str = None

    def bit(self):
        return 1 << self.bit_index

    def get_resource_permission_key(self, resource_id):
        workspace = f":w:{self.workspace_id}" if self.workspace_id else ""
        resource = f":r:{self.resource_id}" if self.resource_id else ""
        return f"{self.group}{workspace}{resource}"

    def __str__(self):
        sub = f"_{self.sub_group}" if self.sub_group != self.group else ""
        flag = f"_{self.flag}" if self.flag else ""
        return f"{self.group}{sub}_{self.operate}{flag}"


@dataclass
class PermissionMeta:
    role_list: list = field(default_factory=list)
    category: Optional[Category] = None
    resource_permission_group_list: Optional[list] = None
    scope: list[PermissionScopeConstants] = field(default_factory=list)
    is_ee: bool = False


@dataclass(frozen=True)
class Role:
    name: str
    workspace_id: str = None

    def __str__(self):
        return f"{self.name}{(':' + self.workspace_id) if self.workspace_id else ''}"

    def __eq__(self, other):
        return str(self) == str(other)


@dataclass(frozen=True)
class RoleMeta:
    desc: str
    group: RoleGroup
