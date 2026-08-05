# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： role_constants.py
    @date：2026/8/4 9:50
    @desc:
"""
from enum import Enum

from common.auth.constants.role_group import RoleGroup
from common.auth.struct.permission import Role, RoleMeta


class RoleConstants(Enum):
    ADMIN = (Role("ADMIN"), RoleMeta('系统管理员', RoleGroup.SYSTEM_USER))
    WORKSPACE_MANAGE = (Role("WORKSPACE_MANAGE"), RoleMeta('工作空间管理员', RoleGroup.SYSTEM_USER))
    USER = (Role("USER"), RoleMeta('普通用户', RoleGroup.SYSTEM_USER))
    EXTENDS_ADMIN = (Role("EXTENDS_ADMIN"), RoleMeta('继承系统管理员', RoleGroup.SYSTEM_USER))
    EXTENDS_WORKSPACE_MANAGE = (Role("EXTENDS_WORKSPACE_MANAGE"), RoleMeta('继承工作空间管理员', RoleGroup.SYSTEM_USER))
    EXTENDS_USER = (Role("EXTENDS_USER"), RoleMeta('继承普通用户', RoleGroup.SYSTEM_USER))

    CHAT_ANONYMOUS_USER = (Role("CHAT_ANONYMOUS_USER"), RoleMeta('对话匿名用户', RoleGroup.CHAT_USER))
    CHAT_USER = (Role("CHAT_USER"), RoleMeta('对话用户', RoleGroup.CHAT_USER))

    def __init__(self, value, meta):
        self._value_ = value
        self.meta = meta

    def __str__(self):
        return self.value.__str__()

    def get_workspace_role(self):
        return lambda r, kwargs: Role(self.value.name, kwargs.get('workspace_id'))
