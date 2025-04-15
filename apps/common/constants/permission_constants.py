"""
    @project: qabot
    @Author：虎虎
    @file： permission_constants.py
    @date：2023/9/13 18:23
    @desc: 权限,角色 常量
"""
from enum import Enum
from typing import List


class Group(Enum):
    """
    权限组 一个组一般对应前端一个菜单
    """
    USER = "USER"


class Operate(Enum):
    """
     一个权限组的操作权限
    """
    READ = 'READ'
    EDIT = "EDIT"
    CREATE = "CREATE"
    DELETE = "DELETE"
    """
    使用权限
    """
    USE = "USE"


class RoleGroup(Enum):
    # 系统用户
    SYSTEM_USER = "SYSTEM_USER"
    # 对话用户
    CHAT_USER = "CHAT_USER"


class Role:
    def __init__(self, name: str, decs: str, group: RoleGroup):
        self.name = name
        self.decs = decs
        self.group = group


class RoleConstants(Enum):
    ADMIN = Role("ADMIN", '超级管理员', RoleGroup.SYSTEM_USER)
    WORKSPACE_MANAGE = Role("WORKSPACE_MANAGE", '工作空间管理员', RoleGroup.SYSTEM_USER)
    USER = Role("USER", '普通用户', RoleGroup.SYSTEM_USER)


class Permission:
    """
    权限信息
    """

    def __init__(self, group: Group, operate: Operate, dynamic_tag=None, role_list=None):
        if role_list is None:
            role_list = []
        self.group = group
        self.operate = operate
        self.dynamic_tag = dynamic_tag
        # 用于获取角色与权限的关系,只适用于没有权限管理的
        self.role_list = role_list

    @staticmethod
    def new_instance(permission_str: str):
        permission_split = permission_str.split(":")
        group = Group[permission_split[0]]
        operate = Operate[permission_split[2]]
        if len(permission_split) > 2:
            dynamic_tag = ":".join(permission_split[2:])
            return Permission(group, operate, dynamic_tag)
        return Permission(group, operate)

    def __str__(self):
        return self.group.value + ":" + self.operate.value + (
            (":" + self.dynamic_tag) if self.dynamic_tag is not None else '')

    def __eq__(self, other):
        return str(self) == str(other)


class PermissionConstants(Enum):
    """
     权限枚举
    """
    USER_READ = Permission(group=Group.USER, operate=Operate.READ, role_list=[RoleConstants.ADMIN,
                                                                              RoleConstants.USER])
    USER_EDIT = Permission(group=Group.USER, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN])
    USER_DELETE = Permission(group=Group.USER, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN])


def get_default_permission_list_by_role(role: RoleConstants):
    """
    根据角色 获取角色对应的权限
    :param role: 角色
    :return: 权限
    """
    return list(map(lambda k: PermissionConstants[k],
                    list(filter(lambda k: PermissionConstants[k].value.role_list.__contains__(role),
                                PermissionConstants.__members__))))


class Auth:
    """
     用于存储当前用户的角色和权限
    """

    def __init__(self,
                 work_space_list: List,
                 current_workspace,
                 current_role_list: List[Role],
                 permission_list: List[PermissionConstants | Permission],
                 **keywords):
        # 当前用户所有工作空间
        self.work_space_list = work_space_list
        # 当前工作空间
        self.current_workspace = current_workspace
        # 当前工作空间的所有权限+非工作空间权限
        self.permission_list = permission_list
        # 当前工作空间角色列表
        self.current_role_list = current_role_list
        self.keywords = keywords


class CompareConstants(Enum):
    # 或者
    OR = "OR"
    # 并且
    AND = "AND"


class ViewPermission:
    def __init__(self, roleList: List[RoleConstants], permissionList: List[PermissionConstants | object],
                 compare=CompareConstants.OR):
        self.roleList = roleList
        self.permissionList = permissionList
        self.compare = compare
