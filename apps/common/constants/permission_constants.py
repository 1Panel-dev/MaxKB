"""
    @project: qabot
    @Author：虎
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

    DATASET = "DATASET"

    APPLICATION = "APPLICATION"

    SETTING = "SETTING"

    MODEL = "MODEL"

    TEAM = "TEAM"


class Operate(Enum):
    """
     一个权限组的操作权限
    """
    READ = 'READ'
    EDIT = "EDIT"
    CREATE = "CREATE"
    DELETE = "DELETE"
    """
    管理权限
    """
    MANAGE = "MANAGE"
    """
    使用权限
    """
    USE = "USE"


class RoleGroup(Enum):
    USER = 'USER'
    APPLICATION_KEY = "APPLICATION_KEY"
    APPLICATION_ACCESS_TOKEN = "APPLICATION_ACCESS_TOKEN"


class Role:
    def __init__(self, name: str, decs: str, group: RoleGroup):
        self.name = name
        self.decs = decs
        self.group = group


class RoleConstants(Enum):
    ADMIN = Role("管理员", "管理员,预制目前不会使用", RoleGroup.USER)
    USER = Role("用户", "用户所有权限", RoleGroup.USER)
    APPLICATION_ACCESS_TOKEN = Role("会话", "只拥有应用会话框接口权限", RoleGroup.APPLICATION_ACCESS_TOKEN),
    APPLICATION_KEY = Role("应用私钥", "应用私钥", RoleGroup.APPLICATION_KEY)


class Permission:
    """
    权限信息
    """

    def __init__(self, group: Group, operate: Operate, roles=None, dynamic_tag=None):
        if roles is None:
            roles = []
        self.group = group
        self.operate = operate
        self.roleList = roles
        self.dynamic_tag = dynamic_tag

    def __str__(self):
        return self.group.value + ":" + self.operate.value + (
            (":" + self.dynamic_tag) if self.dynamic_tag is not None else '')

    def __eq__(self, other):
        return str(self) == str(other)


class PermissionConstants(Enum):
    """
     权限枚举
    """
    USER_READ = Permission(group=Group.USER, operate=Operate.READ, roles=[RoleConstants.ADMIN, RoleConstants.USER])
    USER_EDIT = Permission(group=Group.USER, operate=Operate.EDIT, roles=[RoleConstants.ADMIN, RoleConstants.USER])
    USER_DELETE = Permission(group=Group.USER, operate=Operate.DELETE, roles=[RoleConstants.USER])

    DATASET_CREATE = Permission(group=Group.DATASET, operate=Operate.CREATE,
                                roles=[RoleConstants.ADMIN, RoleConstants.USER])

    DATASET_READ = Permission(group=Group.DATASET, operate=Operate.READ,
                              roles=[RoleConstants.ADMIN, RoleConstants.USER])

    DATASET_EDIT = Permission(group=Group.DATASET, operate=Operate.EDIT,
                              roles=[RoleConstants.ADMIN, RoleConstants.USER])

    APPLICATION_READ = Permission(group=Group.APPLICATION, operate=Operate.READ,
                                  roles=[RoleConstants.ADMIN, RoleConstants.USER])

    APPLICATION_CREATE = Permission(group=Group.APPLICATION, operate=Operate.CREATE,
                                    roles=[RoleConstants.ADMIN, RoleConstants.USER])

    APPLICATION_DELETE = Permission(group=Group.APPLICATION, operate=Operate.DELETE,
                                    roles=[RoleConstants.ADMIN, RoleConstants.USER])

    APPLICATION_EDIT = Permission(group=Group.APPLICATION, operate=Operate.EDIT,
                                  roles=[RoleConstants.ADMIN, RoleConstants.USER])

    SETTING_READ = Permission(group=Group.SETTING, operate=Operate.READ,
                              roles=[RoleConstants.ADMIN, RoleConstants.USER])

    MODEL_READ = Permission(group=Group.MODEL, operate=Operate.READ, roles=[RoleConstants.ADMIN, RoleConstants.USER])

    MODEL_EDIT = Permission(group=Group.MODEL, operate=Operate.EDIT, roles=[RoleConstants.ADMIN, RoleConstants.USER])

    MODEL_DELETE = Permission(group=Group.MODEL, operate=Operate.DELETE,
                              roles=[RoleConstants.ADMIN, RoleConstants.USER])
    MODEL_CREATE = Permission(group=Group.MODEL, operate=Operate.CREATE,
                              roles=[RoleConstants.ADMIN, RoleConstants.USER])

    TEAM_READ = Permission(group=Group.TEAM, operate=Operate.READ, roles=[RoleConstants.ADMIN, RoleConstants.USER])

    TEAM_CREATE = Permission(group=Group.TEAM, operate=Operate.CREATE, roles=[RoleConstants.ADMIN, RoleConstants.USER])

    TEAM_DELETE = Permission(group=Group.TEAM, operate=Operate.DELETE, roles=[RoleConstants.ADMIN, RoleConstants.USER])

    TEAM_EDIT = Permission(group=Group.TEAM, operate=Operate.EDIT, roles=[RoleConstants.ADMIN, RoleConstants.USER])


def get_permission_list_by_role(role: RoleConstants):
    """
    根据角色 获取角色对应的权限
    :param role: 角色
    :return: 权限
    """
    return list(map(lambda k: PermissionConstants[k],
                    list(filter(lambda k: PermissionConstants[k].value.roleList.__contains__(role),
                                PermissionConstants.__members__))))


class Auth:
    """
     用于存储当前用户的角色和权限
    """

    def __init__(self, role_list: List[RoleConstants], permission_list: List[PermissionConstants | Permission]
                 , client_id, client_type, current_role: RoleConstants, **keywords):
        self.role_list = role_list
        self.permission_list = permission_list
        self.client_id = client_id
        self.client_type = client_type
        self.keywords = keywords
        self.current_role = current_role


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
