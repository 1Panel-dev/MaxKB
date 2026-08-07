# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： auth.py
    @date：2026/8/5 9:45
    @desc:
"""
from typing import Dict

from application.models import ChatUserType
from common.auth.constants.role_constants import RoleConstants
from common.auth.struct.permission import Role
from common.constants.authentication_type import UserType


class Auth:
    """
     用于存储当前用户的角色和权限
    """

    def __init__(self,
                 roles: set[RoleConstants | Role | str],
                 permissions: Dict[str, int],
                 **keywords):
        # 权限列表
        self.permissions = permissions
        # 角色列表
        self.roles = roles
        self.keywords = keywords


class Principal:
    def __init__(self, _id,
                 _type: ChatUserType | UserType,
                 profile=None,
                 **keywords):
        self.id = _id
        self._type = _type
        self.profile = profile
        self.keywords = keywords
