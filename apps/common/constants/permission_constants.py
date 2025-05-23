"""
    @project: qabot
    @Author：虎虎
    @file： permission_constants.py
    @date：2023/9/13 18:23
    @desc: 权限,角色 常量
"""
from enum import Enum
from functools import reduce
from typing import List

from django.db import models
from django.utils.translation import gettext as _


class Group(Enum):
    """
    权限组 一个组一般对应前端一个菜单
    """
    USER = "USER_MANAGEMENT"

    APPLICATION = "APPLICATION"

    KNOWLEDGE = "KNOWLEDGE"

    KNOWLEDGE_DOCUMENT = "KNOWLEDGE_DOCUMENT"

    KNOWLEDGE_PROBLEM = "KNOWLEDGE_PROBLEM"

    MODEL = "MODEL"

    TOOL = "TOOL"

    WORKSPACE_USER_RESOURCE_PERMISSION = "WORKSPACE_USER_RESOURCE_PERMISSION"

    EMAIL_SETTING = "EMAIL_SETTING"
    ROLE = "ROLE"
    WORKSPACE = "WORKSPACE"


class SystemGroup(Enum):
    """
    一级菜单
    """
    USER_MANAGEMENT = "USER_MANAGEMENT"
    ROLE = "ROLE"
    WORKSPACE = "WORKSPACE"
    RESOURCE_APPLICATION = "RESOURCE_APPLICATION"
    RESOURCE_KNOWLEDGE = "RESOURCE_KNOWLEDGE"
    RESOURCE_TOOL = "RESOURCE_TOOL"
    RESOURCE_MODEL = "RESOURCE_MODEL"
    RESOURCE_PERMISSION = "RESOURCE_PERMISSION"
    SHARED_KNOWLEDGE = "SHARED_KNOWLEDGE"
    SHARED_MODEL = "SHARED_MODEL"
    SHARED_TOOL = "SHARED_TOOL"
    SYSTEM_SETTING = "SYSTEM_SETTING"
    OPERATION_LOG = "OPERATION_LOG"
    OTHER = "OTHER"


class WorkspaceGroup(Enum):
    SYSTEM_MANAGEMENT = "SYSTEM_MANAGEMENT"
    APPLICATION = "APPLICATION"
    KNOWLEDGE = "KNOWLEDGE"
    MODEL = "MODEL"
    TOOL = "TOOL"
    OTHER = "OTHER"


class UserGroup(Enum):
    APPLICATION = "APPLICATION"
    KNOWLEDGE = "KNOWLEDGE"
    MODEL = "MODEL"
    TOOL = "TOOL"
    OTHER = "OTHER"


class Operate(Enum):
    """
     一个权限组的操作权限
    """
    READ = 'READ'
    EDIT = "READ+EDIT"
    CREATE = "READ+CREATE"
    DELETE = "READ+DELETE"
    """
    使用权限
    """
    USE = "USE"
    IMPORT = "READ+IMPORT"
    EXPORT = "READ+EXPORT"  # 导入导出
    DEBUG = "READ+DEBUG"  # 调试
    SYNC = "READ+SYNC"  # 同步
    GENERATE = "READ+GENERATE"  # 生成
    ADD_MEMBER = "READ+ADD_MEMBER"  # 添加成员
    REMOVE_MEMBER = "READ+REMOVE_MEMBER"  # 添加成员
    VECTOR = "READ+VECTOR"  # 向量化
    MIGRATE = "READ+MIGRATE"  # 迁移
    RELATE = "READ+RELATE"  # 关联


class RoleGroup(Enum):
    # 系统用户
    SYSTEM_USER = "SYSTEM_USER"
    # 对话用户
    CHAT_USER = "CHAT_USER"


class ResourcePermissionRole(models.TextChoices):
    """
    资源权限根据角色
    """
    ROLE = "ROLE"

    def __eq__(self, other):
        return str(self) == str(other)


class ResourcePermissionGroup(models.TextChoices):
    """
    资源权限组
    """
    # 查看
    VIEW = "VIEW"
    # 管理
    MANAGE = "MANAGE"

    def __eq__(self, other):
        return str(self) == str(other)


class ResourceAuthType(models.TextChoices):
    """
    资源授权类型
    """
    "当授权类型是Role时候"
    ROLE = "ROLE"

    """资源权限组"""
    RESOURCE_PERMISSION_GROUP = "RESOURCE_PERMISSION_GROUP"


class Role:
    def __init__(self, name: str, decs: str, group: RoleGroup, resource_path=None):
        self.name = name
        self.decs = decs
        self.group = group
        self.resource_path = resource_path

    def __str__(self):
        return self.name + (
            (":" + self.resource_path) if self.resource_path is not None else '')

    def __eq__(self, other):
        return str(self) == str(other)


class RoleConstants(Enum):
    ADMIN = Role("ADMIN", '超级管理员', RoleGroup.SYSTEM_USER)
    WORKSPACE_MANAGE = Role("WORKSPACE_MANAGE", '工作空间管理员', RoleGroup.SYSTEM_USER)
    USER = Role("USER", '普通用户', RoleGroup.SYSTEM_USER)

    def get_workspace_role(self):
        return lambda r, kwargs: Role(name=self.value.name,
                                      decs=self.value.decs,
                                      group=self.value.group,
                                      resource_path=
                                      f"/WORKSPACE/{kwargs.get('workspace_id')}")


Permission_Label = {
    SystemGroup.SYSTEM_SETTING.value: _("System Setting"),
    SystemGroup.USER_MANAGEMENT.value: _("User Management"),
    SystemGroup.ROLE.value: _("Role"),
    SystemGroup.WORKSPACE.value: _("Workspace"),
    SystemGroup.RESOURCE_APPLICATION.value: _("Resource Application"),
    SystemGroup.RESOURCE_KNOWLEDGE.value: _("Resource Knowledge"),
    SystemGroup.RESOURCE_TOOL.value: _("Resource Tool"),
    SystemGroup.RESOURCE_MODEL.value: _("Resource Model"),
    SystemGroup.RESOURCE_PERMISSION.value: _("Resource Permission"),
    SystemGroup.SHARED_KNOWLEDGE.value: _("Shared Knowledge"),
    SystemGroup.SHARED_MODEL.value: _("Shared Model"),
    SystemGroup.SHARED_TOOL.value: _("Shared Tool"),
    SystemGroup.OPERATION_LOG.value: _("Operation Log"),
    SystemGroup.OTHER.value: _("Other"),
    WorkspaceGroup.SYSTEM_MANAGEMENT.value: _("System Management"),
    WorkspaceGroup.APPLICATION.value: _("Application"),
    WorkspaceGroup.KNOWLEDGE.value: _("Knowledge"),
    WorkspaceGroup.MODEL.value: _("Model"),
    WorkspaceGroup.TOOL.value: _("Tool"),
    WorkspaceGroup.OTHER.value: _("Other"),
    Operate.READ.value: _("Read"),
    Operate.EDIT.value: _("Edit"),
    Operate.CREATE.value: _("Create"),
    Operate.DELETE.value: _("Delete"),
    Group.EMAIL_SETTING.value: _("Email Setting"),
    Group.APPLICATION.value: _("Application"),
    Group.KNOWLEDGE.value: _("Knowledge"),
    Group.KNOWLEDGE_DOCUMENT.value: _("Document"),
    Group.KNOWLEDGE_PROBLEM.value: _("Problem"),
    Operate.IMPORT.value: _("Import"),
    Operate.EXPORT.value: _("Export"),
    Operate.DEBUG.value: _("Debug"),
    Operate.SYNC.value: _("Sync"),
    Operate.GENERATE.value: _("Generate"),
    Operate.ADD_MEMBER.value: _("Add Member"),
    Operate.REMOVE_MEMBER.value: _("Remove Member"),
    Operate.VECTOR.value: _("Vector"),
    Operate.MIGRATE.value: _("Migrate"),
    Operate.RELATE.value: _("Relate"),

}


class Permission:
    """
    权限信息
    """

    def __init__(self, group: Group, operate: Operate, resource_path=None, role_list=None,
                 resource_permission_group_list=None, parent_group=None, label=None):
        if role_list is None:
            role_list = []
        if resource_permission_group_list is None:
            resource_permission_group_list = []
        self.group = group
        self.operate = operate
        self.resource_path = resource_path
        # 用于获取角色与权限的关系,只适用于没有权限管理的
        self.role_list = role_list
        # 用于资源权限权限分组
        self.resource_permission_group_list = resource_permission_group_list
        self.parent_group = parent_group  # 新增字段：父级组
        self.label = label

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
            (":" + self.resource_path) if self.resource_path is not None else '')

    def __eq__(self, other):
        return str(self) == str(other)


class PermissionConstants(Enum):
    """
     权限枚举
    """
    USER_READ = Permission(
        group=Group.USER, operate=Operate.READ, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[SystemGroup.USER_MANAGEMENT]
    )
    USER_CREATE = Permission(
        group=Group.USER, operate=Operate.CREATE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.USER_MANAGEMENT]
    )
    USER_EDIT = Permission(
        group=Group.USER, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.USER_MANAGEMENT]
    )
    USER_DELETE = Permission(
        group=Group.USER, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.USER_MANAGEMENT]
    )

    MODEL_CREATE = Permission(
        group=Group.MODEL, operate=Operate.CREATE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.MODEL, UserGroup.MODEL]
    )
    MODEL_READ = Permission(
        group=Group.MODEL, operate=Operate.READ, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.MODEL, UserGroup.MODEL]
    )
    MODEL_EDIT = Permission(
        group=Group.MODEL, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.MODEL, UserGroup.MODEL]
    )
    MODEL_DELETE = Permission(
        group=Group.MODEL, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.MODEL, UserGroup.MODEL]
    )
    TOOL_CREATE = Permission(
        group=Group.TOOL, operate=Operate.CREATE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.TOOL, UserGroup.TOOL]
    )
    TOOL_EDIT = Permission(
        group=Group.TOOL, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.TOOL, UserGroup.TOOL]
    )
    TOOL_READ = Permission(
        group=Group.TOOL, operate=Operate.READ, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.TOOL, UserGroup.TOOL]
    )
    TOOL_DELETE = Permission(
        group=Group.TOOL, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.TOOL, UserGroup.TOOL]
    )
    TOOL_DEBUG = Permission(
        group=Group.TOOL, operate=Operate.DEBUG, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.TOOL, UserGroup.TOOL]
    )
    TOOL_IMPORT = Permission(
        group=Group.TOOL, operate=Operate.IMPORT, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.TOOL, UserGroup.TOOL]
    )
    TOOL_EXPORT = Permission(
        group=Group.TOOL, operate=Operate.EXPORT, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.TOOL, UserGroup.TOOL]
    )
    KNOWLEDGE_READ = Permission(
        group=Group.KNOWLEDGE, operate=Operate.READ, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionGroup.VIEW],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_CREATE = Permission(
        group=Group.KNOWLEDGE, operate=Operate.CREATE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_EDIT = Permission(
        group=Group.KNOWLEDGE, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DELETE = Permission(
        group=Group.KNOWLEDGE, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_SYNC = Permission(
        group=Group.KNOWLEDGE, operate=Operate.SYNC, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_EXPORT = Permission(
        group=Group.KNOWLEDGE, operate=Operate.EXPORT, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_VECTOR = Permission(
        group=Group.KNOWLEDGE, operate=Operate.VECTOR, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_GENERATE = Permission(
        group=Group.KNOWLEDGE, operate=Operate.GENERATE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_READ = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.READ,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_CREATE = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.CREATE,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_EDIT = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_DELETE = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_SYNC = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.SYNC, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_EXPORT = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.EXPORT,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_GENERATE = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.GENERATE,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_VECTOR = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.VECTOR,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_MIGRATE = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.MIGRATE,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )

    KNOWLEDGE_PROBLEM_READ = Permission(
        group=Group.KNOWLEDGE_PROBLEM, operate=Operate.READ,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_PROBLEM_CREATE = Permission(
        group=Group.KNOWLEDGE_PROBLEM, operate=Operate.CREATE,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_PROBLEM_EDIT = Permission(
        group=Group.KNOWLEDGE_PROBLEM, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_PROBLEM_DELETE = Permission(
        group=Group.KNOWLEDGE_PROBLEM, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_PROBLEM_RELATE = Permission(
        group=Group.KNOWLEDGE_PROBLEM, operate=Operate.RELATE,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    WORKSPACE_USER_RESOURCE_PERMISSION_READ = Permission(
        group=Group.WORKSPACE_USER_RESOURCE_PERMISSION, operate=Operate.READ,
        role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE]
    )
    EMAIL_SETTING_READ = Permission(
        group=Group.EMAIL_SETTING, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=SystemGroup.SYSTEM_SETTING
    )
    EMAIL_SETTING_EDIT = Permission(
        group=Group.EMAIL_SETTING, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=SystemGroup.SYSTEM_SETTING
    )

    ROLE_READ = Permission(
        group=Group.ROLE, operate=Operate.READ, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[SystemGroup.ROLE, WorkspaceGroup.SYSTEM_MANAGEMENT]
    )
    ROLE_CREATE = Permission(
        group=Group.ROLE, operate=Operate.CREATE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.ROLE]
    )
    ROLE_EDIT = Permission(
        group=Group.ROLE, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.ROLE]
    )
    ROLE_DELETE = Permission(
        group=Group.ROLE, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.ROLE]
    )
    ROLE_ADD_MEMBER = Permission(
        group=Group.ROLE, operate=Operate.ADD_MEMBER, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.ROLE]
    )
    ROLE_REMOVE_MEMBER = Permission(
        group=Group.ROLE, operate=Operate.REMOVE_MEMBER, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.ROLE]
    )

    WORKSPACE_ROLE_ADD_MEMBER = Permission(
        group=Group.ROLE, operate=Operate.ADD_MEMBER, role_list=[RoleConstants.ADMIN],
        parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
    )
    WORKSPACE_ROLE_REMOVE_MEMBER = Permission(
        group=Group.ROLE, operate=Operate.REMOVE_MEMBER, role_list=[RoleConstants.ADMIN],
        parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
    )
    WORKSPACE_ROLE_READ = Permission(
        group=Group.ROLE, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
    )

    WORKSPACE_READ = Permission(
        group=Group.WORKSPACE, operate=Operate.READ, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[SystemGroup.WORKSPACE]
    )
    WORKSPACE_CREATE = Permission(
        group=Group.WORKSPACE, operate=Operate.CREATE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.WORKSPACE]
    )
    WORKSPACE_EDIT = Permission(
        group=Group.WORKSPACE, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.WORKSPACE]
    )
    WORKSPACE_DELETE = Permission(
        group=Group.WORKSPACE, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.WORKSPACE]
    )
    WORKSPACE_ADD_MEMBER = Permission(
        group=Group.WORKSPACE, operate=Operate.ADD_MEMBER, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.WORKSPACE]
    )
    WORKSPACE_REMOVE_MEMBER = Permission(
        group=Group.WORKSPACE, operate=Operate.REMOVE_MEMBER, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.WORKSPACE]
    )
    WORKSPACE_WORKSPACE_READ = Permission(
        group=Group.WORKSPACE, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
    )
    WORKSPACE_WORKSPACE_ADD_MEMBER = Permission(
        group=Group.WORKSPACE, operate=Operate.ADD_MEMBER, role_list=[RoleConstants.ADMIN],
        parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
    )
    WORKSPACE_WORKSPACE_REMOVE_MEMBER = Permission(
        group=Group.WORKSPACE, operate=Operate.REMOVE_MEMBER, role_list=[RoleConstants.ADMIN],
        parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
    )

    def get_workspace_application_permission(self):
        return lambda r, kwargs: Permission(group=self.value.group, operate=self.value.operate,
                                            resource_path=
                                            f"/WORKSPACE/{kwargs.get('workspace_id')}/APPLICATION/{kwargs.get('application_id')}")

    def get_workspace_knowledge_permission(self):
        return lambda r, kwargs: Permission(group=self.value.group, operate=self.value.operate,
                                            resource_path=
                                            f"/WORKSPACE/{kwargs.get('workspace_id')}/KNOWLEDGE/{kwargs.get('knowledge_id')}")

    def get_workspace_permission(self):
        return lambda r, kwargs: Permission(group=self.value.group, operate=self.value.operate,
                                            resource_path=
                                            f"/WORKSPACE/{kwargs.get('workspace_id')}")

    def __eq__(self, other):
        if isinstance(other, PermissionConstants):
            return other == self
        else:
            return self.value == other


def get_default_permission_list_by_role(role: RoleConstants):
    """
    根据角色 获取角色对应的权限
    :param role: 角色
    :return: 权限
    """
    return list(map(lambda k: PermissionConstants[k],
                    list(filter(lambda k: PermissionConstants[k].value.role_list.__contains__(role),
                                PermissionConstants.__members__))))


class RolePermissionMapping:
    def __init__(self, role_id, permission_id):
        self.role_id = role_id
        self.permission_id = permission_id


class WorkspaceUserRoleMapping:
    def __init__(self, workspace_id, role_id, user_id):
        self.workspace_id = workspace_id
        self.role_id = role_id
        self.user_id = user_id


def get_default_role_permission_mapping_list():
    role_permission_mapping_list = [
        [RolePermissionMapping(role.value.name, PermissionConstants[k].value.__str__()) for role in
         PermissionConstants[k].value.role_list] for k in PermissionConstants.__members__]
    return reduce(lambda x, y: [*x, *y], role_permission_mapping_list, [])


def get_default_workspace_user_role_mapping_list(user_role_list: list):
    return [WorkspaceUserRoleMapping('default', role.value.name, 'default') for role in RoleConstants if
            user_role_list.__contains__(role.value.name)]


def get_permission_list_by_resource_group(resource_group: ResourcePermissionGroup):
    """
    根据资源组获取权限
    """
    return [PermissionConstants[k] for k in PermissionConstants.__members__ if
            PermissionConstants[k].value.resource_permission_group_list.__contains__(resource_group)]


class Auth:
    """
     用于存储当前用户的角色和权限
    """

    def __init__(self,
                 current_role_list: List[Role],
                 permission_list: List[PermissionConstants | Permission],
                 **keywords):
        # 权限列表
        self.permission_list = permission_list
        # 角色列表
        self.role_list = current_role_list
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
