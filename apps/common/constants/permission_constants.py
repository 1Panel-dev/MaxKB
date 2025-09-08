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
from django.utils.translation import gettext_lazy as _

from maxkb import settings


class Group(Enum):
    """
    权限组 一个组一般对应前端一个菜单
    """

    USER = "USER_MANAGEMENT"
    # 应用
    APPLICATION = "APPLICATION"
    # 应用概览
    APPLICATION_OVERVIEW = "APPLICATION_OVERVIEW"
    # 应用接入
    APPLICATION_ACCESS = "APPLICATION_ACCESS"
    # 应用 对话用户
    APPLICATION_CHAT_USER = "APPLICATION_CHAT_USER"
    # 知识库 对话用户
    KNOWLEDGE_CHAT_USER = "KNOWLEDGE_CHAT_USER"
    # 应用对话日志
    APPLICATION_CHAT_LOG = "APPLICATION_CHAT_LOG"

    KNOWLEDGE = "KNOWLEDGE"
    SYSTEM_KNOWLEDGE = "SYSTEM_KNOWLEDGE"
    SYSTEM_RES_KNOWLEDGE = "SYSTEM_RESOURCE_KNOWLEDGE"
    KNOWLEDGE_HIT_TEST = "KNOWLEDGE_HIT_TEST"
    KNOWLEDGE_DOCUMENT = "KNOWLEDGE_DOCUMENT"
    SYSTEM_KNOWLEDGE_DOCUMENT = "SYSTEM_KNOWLEDGE_DOCUMENT"
    SYSTEM_RES_KNOWLEDGE_DOCUMENT = "SYSTEM_RESOURCE_KNOWLEDGE_DOCUMENT"

    KNOWLEDGE_PROBLEM = "KNOWLEDGE_PROBLEM"
    SYSTEM_KNOWLEDGE_PROBLEM = "SYSTEM_KNOWLEDGE_PROBLEM"
    SYSTEM_RES_KNOWLEDGE_PROBLEM = "SYSTEM_RESOURCE_KNOWLEDGE_PROBLEM"

    SYSTEM_KNOWLEDGE_HIT_TEST = "SYSTEM_KNOWLEDGE_HIT_TEST"
    SYSTEM_RES_KNOWLEDGE_HIT_TEST = "SYSTEM_RESOURCE_KNOWLEDGE_HIT_TEST"
    SYSTEM_KNOWLEDGE_CHAT_USER = "SYSTEM_KNOWLEDGE_CHAT_USER"
    SYSTEM_RES_KNOWLEDGE_CHAT_USER = "SYSTEM_RESOURCE_KNOWLEDGE_CHAT_USER"

    MODEL = "MODEL"
    SYSTEM_MODEL = "SYSTEM_MODEL"
    SYSTEM_RES_MODEL = "SYSTEM_RESOURCE_MODEL"
    SYSTEM_RES_APPLICATION = "SYSTEM_RESOURCE_APPLICATION"
    SYSTEM_RES_APPLICATION_OVERVIEW = "SYSTEM_RESOURCE_APPLICATION_OVERVIEW"
    SYSTEM_RES_APPLICATION_ACCESS = "SYSTEM_RESOURCE_APPLICATION_ACCESS"
    SYSTEM_RES_APPLICATION_CHAT_USER = "SYSTEM_RESOURCE_APPLICATION_CHAT_USER"
    SYSTEM_RES_APPLICATION_CHAT_LOG = "SYSTEM_RESOURCE_APPLICATION_CHAT_LOG"

    TOOL = "TOOL"
    SYSTEM_TOOL = "SYSTEM_TOOL"
    SYSTEM_RES_TOOL = "SYSTEM_RESOURCE_TOOL"

    APPLICATION_WORKSPACE_USER_RESOURCE_PERMISSION = "APPLICATION_WORKSPACE_USER_RESOURCE_PERMISSION"
    KNOWLEDGE_WORKSPACE_USER_RESOURCE_PERMISSION = "KNOWLEDGE_WORKSPACE_USER_RESOURCE_PERMISSION"
    TOOL_WORKSPACE_USER_RESOURCE_PERMISSION = "TOOL_WORKSPACE_USER_RESOURCE_PERMISSION"
    MODEL_WORKSPACE_USER_RESOURCE_PERMISSION = "MODEL_WORKSPACE_USER_RESOURCE_PERMISSION"

    EMAIL_SETTING = "EMAIL_SETTING"
    ROLE = "ROLE"
    WORKSPACE_ROLE = "WORKSPACE_ROLE"
    WORKSPACE = "WORKSPACE"
    WORKSPACE_WORKSPACE = "WORKSPACE_WORKSPACE"

    DISPLAY_SETTINGS = "DISPLAY_SETTINGS"
    LOGIN_AUTH = "LOGIN_AUTH"
    SYSTEM_API_KEY = "SYSTEM_API_KEY"
    APPEARANCE_SETTINGS = "APPEARANCE_SETTINGS"
    CHAT_USER = "CHAT_USER"
    WORKSPACE_CHAT_USER = "WORKSPACE_CHAT_USER"
    USER_GROUP = "USER_GROUP"
    WORKSPACE_USER_GROUP = "WORKSPACE_USER_GROUP"
    CHAT_USER_AUTH = "CHAT_USER_AUTH"
    OTHER = "OTHER"
    OVERVIEW = "OVERVIEW"
    OPERATION_LOG = "OPERATION_LOG"


class SystemGroup(Enum):
    """
    一级菜单
    """
    USER_MANAGEMENT = "USER_MANAGEMENT"
    ROLE = "ROLE"
    WORKSPACE = "WORKSPACE"
    # RESOURCE = "RESOURCE"
    RESOURCE_APPLICATION = "RESOURCE_APPLICATION"
    RESOURCE_KNOWLEDGE = "RESOURCE_KNOWLEDGE"
    RESOURCE_TOOL = "RESOURCE_TOOL"
    RESOURCE_MODEL = "RESOURCE_MODEL"
    RESOURCE_PERMISSION = "RESOURCE_PERMISSION"
    SHARED_KNOWLEDGE = "SHARED_KNOWLEDGE"
    SHARED_MODEL = "SHARED_MODEL"
    SHARED_TOOL = "SHARED_TOOL"
    CHAT_USER = "CHAT_USER"
    SYSTEM_SETTING = "SYSTEM_SETTING"
    OPERATION_LOG = "OPERATION_LOG"
    OTHER = "OTHER"


class WorkspaceGroup(Enum):
    SYSTEM_MANAGEMENT = "SYSTEM_MANAGEMENT"
    APPLICATION = "APPLICATION"
    KNOWLEDGE = "KNOWLEDGE"
    MODEL = "MODEL"
    TOOL = "TOOL"
    RESOURCE_PERMISSION = "RESOURCE_PERMISSION"
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
    SELF = ""
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
    USER_GROUP = "READ+USER_GROUP"  # 用户组
    ANNOTATION = "READ+ANNOTATION"  # 标注
    CLEAR_POLICY = "READ+CLEAR_POLICY"
    EMBED = "READ+EMBED"  # 嵌入
    ACCESS = "READ+ACCESS"  # 访问限制
    DISPLAY = "READ+DISPLAY"  # 显示设置
    API_KEY = "READ+API_KEY"  # API_KEY
    PUBLIC_ACCESS = "READ+PUBLIC_ACCESS"  # 公共访问链接
    Q_WEIXIN = "READ+Q_WEIXIN"  # 企业微信
    FEISHU = "READ+FEISHU"  # 飞书
    DD = "READ+DD"  # 钉钉
    WEIXIN_PUBLIC_ACCOUNT = "READ+WEIXIN_PUBLIC_ACCOUNT"  # 微信公众号
    SLACK = "READ+SLACK"  # SLACK
    ADD_KNOWLEDGE = "READ+ADD_KNOWLEDGE"  # 添加到知识库
    TO_CHAT = "READ+TO_CHAT"  # 去对话
    SETTING = "READ+SETTING"  # 管理
    DOWNLOAD = "READ+DOWNLOAD"  # 下载
    AUTH = "READ+AUTH"


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


class ResourcePermission(models.TextChoices):
    """
    资源权限组
    """
    # 查看
    VIEW = "VIEW"
    # 管理
    MANAGE = "MANAGE"

    def __eq__(self, other):
        return str(self) == str(other)


class Resource(models.TextChoices):
    KNOWLEDGE = Group.KNOWLEDGE.value
    APPLICATION = Group.APPLICATION.value
    TOOL = Group.TOOL.value
    MODEL = Group.MODEL.value

    def __eq__(self, other):
        return str(self) == str(other)


class ResourcePermissionGroup:
    def __init__(self, resource: Resource, permission: ResourcePermission):
        self.permission = permission
        self.resource = resource

    def __eq__(self, other):
        return str(self.permission) == str(other.permission) and str(self.resource) == str(other.resource)


class ResourcePermissionConst:
    KNOWLEDGE_MANGE = ResourcePermissionGroup(Resource.KNOWLEDGE, ResourcePermission.MANAGE)
    KNOWLEDGE_VIEW = ResourcePermissionGroup(Resource.KNOWLEDGE, ResourcePermission.VIEW)
    APPLICATION_MANGE = ResourcePermissionGroup(Resource.APPLICATION, ResourcePermission.MANAGE)
    APPLICATION_VIEW = ResourcePermissionGroup(Resource.APPLICATION, ResourcePermission.VIEW)
    TOOL_MANGE = ResourcePermissionGroup(Resource.TOOL, ResourcePermission.MANAGE)
    TOOL_VIEW = ResourcePermissionGroup(Resource.TOOL, ResourcePermission.VIEW)
    MODEL_MANGE = ResourcePermissionGroup(Resource.MODEL, ResourcePermission.MANAGE)
    MODEL_VIEW = ResourcePermissionGroup(Resource.MODEL, ResourcePermission.VIEW)


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

    def get_workspace_role(self):
        return lambda r, kwargs: Role(self.name, self.decs, self.group,
                                      resource_path=f"/WORKSPACE/{kwargs.get('workspace_id')}")


class RoleConstants(Enum):
    ADMIN = Role("ADMIN", '超级管理员', RoleGroup.SYSTEM_USER)
    WORKSPACE_MANAGE = Role("WORKSPACE_MANAGE", '工作空间管理员', RoleGroup.SYSTEM_USER)
    USER = Role("USER", '普通用户', RoleGroup.SYSTEM_USER)
    CHAT_ANONYMOUS_USER = Role("CHAT_ANONYMOUS_USER", "对话匿名用户", RoleGroup.CHAT_USER)
    CHAT_USER = Role("CHAT_USER", "对话用户", RoleGroup.CHAT_USER)

    EXTENDS_ADMIN = Role("EXTENDS_ADMIN", '继承超级管理员', RoleGroup.SYSTEM_USER)
    EXTENDS_WORKSPACE_MANAGE = Role("EXTENDS_WORKSPACE_MANAGE", "继承工作空间管理员", RoleGroup.CHAT_USER)
    EXTENDS_USER = Role("EXTENDS_USER", "继承普通用户", RoleGroup.CHAT_USER)

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
    Group.KNOWLEDGE_HIT_TEST.value: _("Hit-Test"),
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
    Operate.ANNOTATION.value: _("Annotation"),
    Operate.CLEAR_POLICY.value: _("Clear Policy"),
    Operate.DOWNLOAD.value: _('Download'),
    Operate.EMBED.value: _('Embed third party'),
    Operate.ACCESS.value: _('Access restrictions'),
    Operate.DISPLAY.value: _('Display Settings'),
    Operate.API_KEY.value: _('API KEY'),
    Operate.PUBLIC_ACCESS.value: _('Public access link'),
    Operate.Q_WEIXIN.value: _('Enterprise WeiXin'),
    Operate.FEISHU.value: _('Feishu'),
    Operate.DD.value: _('Dingding'),
    Operate.WEIXIN_PUBLIC_ACCOUNT.value: _('Weixin Public Account'),
    Operate.ADD_KNOWLEDGE.value: _('Add to Knowledge Base'),
    Operate.AUTH.value: _('resource authorization'),
    Group.APPLICATION_OVERVIEW.value: _('Overview'),
    Group.APPLICATION_ACCESS.value: _('Application Access'),
    Group.APPLICATION_CHAT_USER.value: _('Dialogue users'),
    Group.APPLICATION_CHAT_LOG.value: _('Conversation log'),
    Group.KNOWLEDGE_CHAT_USER.value: _('Dialogue users'),

    Group.LOGIN_AUTH.value: _("Login Auth"),
    Group.DISPLAY_SETTINGS.value: _("Display Settings"),
    Group.SYSTEM_API_KEY.value: _("System API Key"),
    Group.APPEARANCE_SETTINGS.value: _("Appearance Settings"),
    Group.CHAT_USER.value: _("Chat User"),
    Group.USER_GROUP.value: _("User Group"),
    Group.CHAT_USER_AUTH.value: _("Chat User Auth"),
    Group.OVERVIEW.value: _("Overview"),
    Group.SYSTEM_TOOL.value: _("Tool"),
    Group.SYSTEM_MODEL.value: _("Model"),
    Group.SYSTEM_KNOWLEDGE.value: _("Knowledge"),
    Group.SYSTEM_KNOWLEDGE_DOCUMENT.value: _("Document"),
    Group.SYSTEM_KNOWLEDGE_PROBLEM.value: _("Problem"),
    Group.SYSTEM_KNOWLEDGE_HIT_TEST.value: _("Hit-Test"),
    Group.SYSTEM_KNOWLEDGE_CHAT_USER.value: _("Dialogue users"),
    Group.SYSTEM_RES_TOOL.value: _("Tool"),
    Group.SYSTEM_RES_MODEL.value: _("Model"),
    Group.SYSTEM_RES_KNOWLEDGE.value: _("Knowledge"),
    Group.SYSTEM_RES_KNOWLEDGE_DOCUMENT.value: _("Document"),
    Group.SYSTEM_RES_KNOWLEDGE_PROBLEM.value: _("Problem"),
    Group.SYSTEM_RES_KNOWLEDGE_HIT_TEST.value: _("Hit-Test"),
    Group.SYSTEM_RES_KNOWLEDGE_CHAT_USER.value: _("Dialogue users"),
    Group.WORKSPACE_USER_GROUP.value: _("User Group"),
    Group.WORKSPACE_CHAT_USER.value: _("Chat User"),
    Group.WORKSPACE_WORKSPACE.value: _("Workspace"),
    Group.WORKSPACE_ROLE.value: _("Role"),
    Group.APPLICATION_WORKSPACE_USER_RESOURCE_PERMISSION.value: _("Application"),
    Group.KNOWLEDGE_WORKSPACE_USER_RESOURCE_PERMISSION.value: _("Knowledge"),
    Group.MODEL_WORKSPACE_USER_RESOURCE_PERMISSION.value: _("Model"),
    Group.TOOL_WORKSPACE_USER_RESOURCE_PERMISSION.value: _("Tool"),
    Group.SYSTEM_RES_APPLICATION.value: _("Application"),
    Group.SYSTEM_RES_APPLICATION_OVERVIEW.value: _("Overview"),
    Group.SYSTEM_RES_APPLICATION_ACCESS.value: _("Application Access"),
    Group.SYSTEM_RES_APPLICATION_CHAT_USER.value: _("Dialogue users"),
    Group.SYSTEM_RES_APPLICATION_CHAT_LOG.value: _("Conversation log"),
    # SystemGroup.RESOURCE.value: _("Resource"),
}


class Permission:
    """
    权限信息
    """

    def __init__(self, group: Group, operate: Operate, resource_path=None, role_list=None,
                 resource_permission_group_list=None, parent_group=None, label=None, is_ee=True):
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
        self.is_ee = is_ee  # 是否是企业版权限

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

        return self.group.value + (
            (":" + self.operate.value) if self.operate.value else '') + (
            (":" + self.resource_path) if self.resource_path is not None else '')

    def __eq__(self, other):
        return str(self) == str(other)


class PermissionConstants(Enum):
    """
     权限枚举
    """
    KNOWLEDGE = Permission(
        group=Group.KNOWLEDGE, operate=Operate.SELF, role_list=[RoleConstants.ADMIN, RoleConstants.USER]
    )
    APPLICATION = Permission(
        group=Group.APPLICATION, operate=Operate.SELF, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
    )
    MODEL = Permission(
        group=Group.MODEL, operate=Operate.SELF, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
    )
    TOOL = Permission(
        group=Group.TOOL, operate=Operate.SELF, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
    )

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

    MODEL_READ = Permission(
        group=Group.MODEL, operate=Operate.READ, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.MODEL, UserGroup.MODEL],
        resource_permission_group_list=[ResourcePermissionConst.MODEL_VIEW]
    )

    MODEL_CREATE = Permission(
        group=Group.MODEL, operate=Operate.CREATE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.MODEL, UserGroup.MODEL],
        resource_permission_group_list=[ResourcePermissionConst.MODEL_MANGE]
    )

    MODEL_EDIT = Permission(
        group=Group.MODEL, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.MODEL, UserGroup.MODEL],
        resource_permission_group_list=[ResourcePermissionConst.MODEL_MANGE]
    )
    MODEL_DELETE = Permission(
        group=Group.MODEL, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.MODEL, UserGroup.MODEL],
        resource_permission_group_list=[ResourcePermissionConst.MODEL_MANGE]
    )
    MODEL_RESOURCE_AUTHORIZATION = Permission(
        group=Group.MODEL, operate=Operate.AUTH, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.MODEL, UserGroup.MODEL],
        resource_permission_group_list=[ResourcePermissionConst.MODEL_MANGE]
    )
    TOOL_READ = Permission(
        group=Group.TOOL, operate=Operate.READ, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.TOOL, UserGroup.TOOL],
        resource_permission_group_list=[ResourcePermissionConst.TOOL_VIEW]
    )

    TOOL_CREATE = Permission(
        group=Group.TOOL, operate=Operate.CREATE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.TOOL, UserGroup.TOOL],
        resource_permission_group_list=[ResourcePermissionConst.TOOL_MANGE]
    )

    TOOL_EDIT = Permission(
        group=Group.TOOL, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.TOOL, UserGroup.TOOL],
        resource_permission_group_list=[ResourcePermissionConst.TOOL_MANGE]
    )

    TOOL_DELETE = Permission(
        group=Group.TOOL, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.TOOL, UserGroup.TOOL],
        resource_permission_group_list=[ResourcePermissionConst.TOOL_MANGE]
    )

    TOOL_DEBUG = Permission(
        group=Group.TOOL, operate=Operate.DEBUG, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.TOOL, UserGroup.TOOL],
        resource_permission_group_list=[ResourcePermissionConst.TOOL_MANGE]
    )
    TOOL_IMPORT = Permission(
        group=Group.TOOL, operate=Operate.IMPORT, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.TOOL, UserGroup.TOOL],
        resource_permission_group_list=[ResourcePermissionConst.TOOL_MANGE]
    )
    TOOL_EXPORT = Permission(
        group=Group.TOOL, operate=Operate.EXPORT, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.TOOL, UserGroup.TOOL],
        resource_permission_group_list=[ResourcePermissionConst.TOOL_MANGE]
    )
    TOOL_RESOURCE_AUTHORIZATION = Permission(
        group=Group.TOOL, operate=Operate.AUTH, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[WorkspaceGroup.TOOL, UserGroup.TOOL],
        resource_permission_group_list=[ResourcePermissionConst.TOOL_MANGE]
    )
    KNOWLEDGE_READ = Permission(
        group=Group.KNOWLEDGE, operate=Operate.READ, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_VIEW],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_CREATE = Permission(
        group=Group.KNOWLEDGE, operate=Operate.CREATE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_VIEW],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_EDIT = Permission(
        group=Group.KNOWLEDGE, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DELETE = Permission(
        group=Group.KNOWLEDGE, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_SYNC = Permission(
        group=Group.KNOWLEDGE, operate=Operate.SYNC, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_EXPORT = Permission(
        group=Group.KNOWLEDGE, operate=Operate.EXPORT, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_VECTOR = Permission(
        group=Group.KNOWLEDGE, operate=Operate.VECTOR, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_GENERATE = Permission(
        group=Group.KNOWLEDGE, operate=Operate.GENERATE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_RESOURCE_AUTHORIZATION = Permission(
        group=Group.KNOWLEDGE, operate=Operate.AUTH, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_READ = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.READ,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_VIEW],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_CREATE = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.CREATE,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_EDIT = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_DELETE = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_SYNC = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.SYNC, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_EXPORT = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.EXPORT,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.DOWNLOAD,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_GENERATE = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.GENERATE,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_VECTOR = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.VECTOR,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_DOCUMENT_MIGRATE = Permission(
        group=Group.KNOWLEDGE_DOCUMENT, operate=Operate.MIGRATE,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_HIT_TEST = Permission(
        group=Group.KNOWLEDGE_HIT_TEST, operate=Operate.READ,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_VIEW],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_PROBLEM_READ = Permission(
        group=Group.KNOWLEDGE_PROBLEM, operate=Operate.READ,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_VIEW],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_PROBLEM_CREATE = Permission(
        group=Group.KNOWLEDGE_PROBLEM, operate=Operate.CREATE,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_PROBLEM_EDIT = Permission(
        group=Group.KNOWLEDGE_PROBLEM, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_PROBLEM_DELETE = Permission(
        group=Group.KNOWLEDGE_PROBLEM, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    KNOWLEDGE_PROBLEM_RELATE = Permission(
        group=Group.KNOWLEDGE_PROBLEM, operate=Operate.RELATE,
        role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
        parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE]
    )
    APPLICATION_WORKSPACE_USER_RESOURCE_PERMISSION_READ = Permission(
        group=Group.APPLICATION_WORKSPACE_USER_RESOURCE_PERMISSION, operate=Operate.READ,
        role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE],
        parent_group=[SystemGroup.RESOURCE_PERMISSION, WorkspaceGroup.RESOURCE_PERMISSION]
    )
    APPLICATION_WORKSPACE_USER_RESOURCE_PERMISSION_EDIT = Permission(
        group=Group.APPLICATION_WORKSPACE_USER_RESOURCE_PERMISSION, operate=Operate.EDIT,
        role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE],
        parent_group=[SystemGroup.RESOURCE_PERMISSION, WorkspaceGroup.RESOURCE_PERMISSION]
    )
    KNOWLEDGE_WORKSPACE_USER_RESOURCE_PERMISSION_READ = Permission(
        group=Group.KNOWLEDGE_WORKSPACE_USER_RESOURCE_PERMISSION, operate=Operate.READ,
        role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE],
        parent_group=[SystemGroup.RESOURCE_PERMISSION, WorkspaceGroup.RESOURCE_PERMISSION]
    )
    KNOWLEDGE_WORKSPACE_USER_RESOURCE_PERMISSION_EDIT = Permission(
        group=Group.KNOWLEDGE_WORKSPACE_USER_RESOURCE_PERMISSION, operate=Operate.EDIT,
        role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE],
        parent_group=[SystemGroup.RESOURCE_PERMISSION, WorkspaceGroup.RESOURCE_PERMISSION]
    )
    TOOL_WORKSPACE_USER_RESOURCE_PERMISSION_READ = Permission(
        group=Group.TOOL_WORKSPACE_USER_RESOURCE_PERMISSION, operate=Operate.READ,
        role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE],
        parent_group=[SystemGroup.RESOURCE_PERMISSION, WorkspaceGroup.RESOURCE_PERMISSION]
    )
    TOOL_WORKSPACE_USER_RESOURCE_PERMISSION_EDIT = Permission(
        group=Group.TOOL_WORKSPACE_USER_RESOURCE_PERMISSION, operate=Operate.EDIT,
        role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE],
        parent_group=[SystemGroup.RESOURCE_PERMISSION, WorkspaceGroup.RESOURCE_PERMISSION]

    )
    MODEL_WORKSPACE_USER_RESOURCE_PERMISSION_READ = Permission(
        group=Group.MODEL_WORKSPACE_USER_RESOURCE_PERMISSION, operate=Operate.READ,
        role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE],
        parent_group=[SystemGroup.RESOURCE_PERMISSION, WorkspaceGroup.RESOURCE_PERMISSION]
    )
    MODEL_WORKSPACE_USER_RESOURCE_PERMISSION_EDIT = Permission(
        group=Group.MODEL_WORKSPACE_USER_RESOURCE_PERMISSION, operate=Operate.EDIT,
        role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE],
        parent_group=[SystemGroup.RESOURCE_PERMISSION, WorkspaceGroup.RESOURCE_PERMISSION]
    )

    EMAIL_SETTING_READ = Permission(
        group=Group.EMAIL_SETTING, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SYSTEM_SETTING]
    )
    EMAIL_SETTING_EDIT = Permission(
        group=Group.EMAIL_SETTING, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SYSTEM_SETTING]
    )

    ROLE_READ = Permission(
        group=Group.ROLE, operate=Operate.READ, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[SystemGroup.ROLE]
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
    WORKSPACE_ROLE_READ = Permission(
        group=Group.WORKSPACE_ROLE, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
    )
    WORKSPACE_ROLE_ADD_MEMBER = Permission(
        group=Group.WORKSPACE_ROLE, operate=Operate.ADD_MEMBER, role_list=[RoleConstants.ADMIN],
        parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
    )
    WORKSPACE_ROLE_REMOVE_MEMBER = Permission(
        group=Group.WORKSPACE_ROLE, operate=Operate.REMOVE_MEMBER, role_list=[RoleConstants.ADMIN],
        parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
    )

    WORKSPACE_READ = Permission(
        group=Group.WORKSPACE, operate=Operate.READ, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[SystemGroup.WORKSPACE], is_ee=settings.edition == "EE"
    )
    WORKSPACE_CREATE = Permission(
        group=Group.WORKSPACE, operate=Operate.CREATE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.WORKSPACE], is_ee=settings.edition == "EE"
    )
    WORKSPACE_EDIT = Permission(
        group=Group.WORKSPACE, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.WORKSPACE], is_ee=settings.edition == "EE"
    )
    WORKSPACE_DELETE = Permission(
        group=Group.WORKSPACE, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.WORKSPACE], is_ee=settings.edition == "EE"
    )
    WORKSPACE_ADD_MEMBER = Permission(
        group=Group.WORKSPACE, operate=Operate.ADD_MEMBER, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.WORKSPACE], is_ee=settings.edition == "EE"
    )
    WORKSPACE_REMOVE_MEMBER = Permission(
        group=Group.WORKSPACE, operate=Operate.REMOVE_MEMBER, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.WORKSPACE], is_ee=settings.edition == "EE"
    )
    WORKSPACE_WORKSPACE_READ = Permission(
        group=Group.WORKSPACE_WORKSPACE, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT], is_ee=settings.edition == "EE"
    )
    WORKSPACE_WORKSPACE_ADD_MEMBER = Permission(
        group=Group.WORKSPACE_WORKSPACE, operate=Operate.ADD_MEMBER, role_list=[RoleConstants.ADMIN],
        parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT], is_ee=settings.edition == "EE"
    )
    WORKSPACE_WORKSPACE_REMOVE_MEMBER = Permission(
        group=Group.WORKSPACE_WORKSPACE, operate=Operate.REMOVE_MEMBER, role_list=[RoleConstants.ADMIN],
        parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT], is_ee=settings.edition == "EE"
    )
    LOGIN_AUTH_READ = Permission(
        group=Group.LOGIN_AUTH, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SYSTEM_SETTING]
    )
    LOGIN_AUTH_EDIT = Permission(
        group=Group.LOGIN_AUTH, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SYSTEM_SETTING]
    )
    APPLICATION_READ = Permission(group=Group.APPLICATION, operate=Operate.READ,
                                  role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                  parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                  resource_permission_group_list=[ResourcePermissionConst.APPLICATION_VIEW],
                                  )
    APPLICATION_DEBUG = Permission(group=Group.APPLICATION, operate=Operate.DEBUG,
                                   role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                   parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                   resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANGE],
                                   )
    APPLICATION_CREATE = Permission(group=Group.APPLICATION, operate=Operate.CREATE,
                                    role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                    parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                    resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANGE],
                                    )
    APPLICATION_IMPORT = Permission(group=Group.APPLICATION, operate=Operate.IMPORT,
                                    role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                    parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                    resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANGE]
                                    )
    APPLICATION_EXPORT = Permission(group=Group.APPLICATION, operate=Operate.EXPORT,
                                    role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                    resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANGE],
                                    parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                    )

    APPLICATION_DELETE = Permission(group=Group.APPLICATION, operate=Operate.DELETE,
                                    role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                    parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                    resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANGE],
                                    )
    APPLICATION_EDIT = Permission(group=Group.APPLICATION, operate=Operate.EDIT,
                                  role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                  parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                  resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANGE],
                                  )
    APPLICATION_RESOURCE_AUTHORIZATION = Permission(group=Group.APPLICATION, operate=Operate.AUTH,
                                                    role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                                    parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                                    resource_permission_group_list=[
                                                        ResourcePermissionConst.APPLICATION_MANGE],
                                                    )
    APPLICATION_OVERVIEW_READ = Permission(group=Group.APPLICATION_OVERVIEW, operate=Operate.READ,
                                           role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                           parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                           resource_permission_group_list=[ResourcePermissionConst.APPLICATION_VIEW],
                                           )

    APPLICATION_OVERVIEW_EMBED = Permission(group=Group.APPLICATION_OVERVIEW, operate=Operate.EMBED,
                                            role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                            parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                            resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANGE],

                                            )

    APPLICATION_OVERVIEW_ACCESS = Permission(group=Group.APPLICATION_OVERVIEW, operate=Operate.ACCESS,
                                             role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                             parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                             resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANGE],

                                             )
    APPLICATION_OVERVIEW_DISPLAY = Permission(group=Group.APPLICATION_OVERVIEW, operate=Operate.DISPLAY,
                                              role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                              parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                              resource_permission_group_list=[
                                                  ResourcePermissionConst.APPLICATION_MANGE],

                                              )
    APPLICATION_OVERVIEW_API_KEY = Permission(group=Group.APPLICATION_OVERVIEW, operate=Operate.API_KEY,
                                              role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                              parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                              resource_permission_group_list=[
                                                  ResourcePermissionConst.APPLICATION_MANGE],

                                              )
    APPLICATION_OVERVIEW_PUBLIC = Permission(group=Group.APPLICATION_OVERVIEW, operate=Operate.PUBLIC_ACCESS,
                                             role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                             parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                             resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANGE],

                                             )
    # 应用接入
    APPLICATION_ACCESS_READ = Permission(group=Group.APPLICATION_ACCESS, operate=Operate.READ,
                                         role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                         parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                         resource_permission_group_list=[ResourcePermissionConst.APPLICATION_VIEW],

                                         )
    APPLICATION_ACCESS_EDIT = Permission(group=Group.APPLICATION_ACCESS, operate=Operate.EDIT,
                                         role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                         parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                         resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANGE])

    APPLICATION_CHAT_USER_READ = Permission(group=Group.APPLICATION_CHAT_USER, operate=Operate.READ,
                                            role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                            parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                            resource_permission_group_list=[ResourcePermissionConst.APPLICATION_VIEW],
                                            )
    APPLICATION_CHAT_USER_EDIT = Permission(group=Group.APPLICATION_CHAT_USER, operate=Operate.EDIT,
                                            role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                            parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                            resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANGE],
                                            )
    KNOWLEDGE_CHAT_USER_READ = Permission(group=Group.KNOWLEDGE_CHAT_USER, operate=Operate.READ,
                                          role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                          parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE],
                                          resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_VIEW],
                                          )

    KNOWLEDGE_CHAT_USER_EDIT = Permission(group=Group.KNOWLEDGE_CHAT_USER, operate=Operate.EDIT,
                                          role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                          parent_group=[WorkspaceGroup.KNOWLEDGE, UserGroup.KNOWLEDGE],
                                          resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANGE],
                                          )

    APPLICATION_CHAT_LOG_READ = Permission(group=Group.APPLICATION_CHAT_LOG, operate=Operate.READ,
                                           role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                           parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                           resource_permission_group_list=[ResourcePermissionConst.APPLICATION_VIEW],
                                           )

    APPLICATION_CHAT_LOG_ANNOTATION = Permission(group=Group.APPLICATION_CHAT_LOG, operate=Operate.ANNOTATION,
                                                 role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                                 parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                                 resource_permission_group_list=[
                                                     ResourcePermissionConst.APPLICATION_MANGE],
                                                 )

    APPLICATION_CHAT_LOG_EXPORT = Permission(group=Group.APPLICATION_CHAT_LOG, operate=Operate.EXPORT,
                                             role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                             parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                             resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANGE],
                                             )

    APPLICATION_CHAT_LOG_CLEAR_POLICY = Permission(group=Group.APPLICATION_CHAT_LOG, operate=Operate.CLEAR_POLICY,
                                                   role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                                   parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                                   resource_permission_group_list=[
                                                       ResourcePermissionConst.APPLICATION_MANGE],
                                                   )
    APPLICATION_CHAT_LOG_ADD_KNOWLEDGE = Permission(group=Group.APPLICATION_CHAT_LOG, operate=Operate.ADD_KNOWLEDGE,
                                                    role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                                    parent_group=[WorkspaceGroup.APPLICATION, UserGroup.APPLICATION],
                                                    resource_permission_group_list=[
                                                        ResourcePermissionConst.APPLICATION_MANGE],
                                                    )

    ABOUT_READ = Permission(group=Group.OTHER, operate=Operate.READ,
                            role_list=[RoleConstants.ADMIN],
                            parent_group=[SystemGroup.OTHER],
                            label=_('About')
                            )
    SWITCH_LANGUAGE = Permission(group=Group.OTHER, operate=Operate.EDIT,
                                 role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                 parent_group=[SystemGroup.OTHER, WorkspaceGroup.OTHER, UserGroup.OTHER],
                                 label=_('Switch Language')
                                 )
    CHANGE_PASSWORD = Permission(group=Group.OTHER, operate=Operate.CREATE,
                                 role_list=[RoleConstants.ADMIN, RoleConstants.USER],
                                 parent_group=[SystemGroup.OTHER, WorkspaceGroup.OTHER, UserGroup.OTHER],
                                 label=_('Change Password')
                                 )

    SYSTEM_API_KEY_EDIT = Permission(group=Group.OTHER, operate=Operate.DELETE,
                                     role_list=[RoleConstants.ADMIN],
                                     parent_group=[SystemGroup.OTHER],
                                     label=_('System API Key')
                                     )

    APPEARANCE_SETTINGS_READ = Permission(group=Group.APPEARANCE_SETTINGS, operate=Operate.READ,
                                          role_list=[RoleConstants.ADMIN],
                                          parent_group=[SystemGroup.SYSTEM_SETTING]
                                          )
    APPEARANCE_SETTINGS_EDIT = Permission(group=Group.APPEARANCE_SETTINGS, operate=Operate.EDIT,
                                          role_list=[RoleConstants.ADMIN],
                                          parent_group=[SystemGroup.SYSTEM_SETTING]
                                          )
    CHAT_USER_READ = Permission(group=Group.CHAT_USER, operate=Operate.READ,
                                role_list=[RoleConstants.ADMIN],
                                parent_group=[SystemGroup.CHAT_USER],
                                )
    CHAT_USER_CREATE = Permission(group=Group.CHAT_USER, operate=Operate.CREATE,
                                  role_list=[RoleConstants.ADMIN],
                                  parent_group=[SystemGroup.CHAT_USER]
                                  )
    CHAT_USER_SYNC = Permission(group=Group.CHAT_USER, operate=Operate.SYNC,
                                role_list=[RoleConstants.ADMIN],
                                parent_group=[SystemGroup.CHAT_USER]
                                )
    CHAT_USER_EDIT = Permission(group=Group.CHAT_USER, operate=Operate.EDIT,
                                role_list=[RoleConstants.ADMIN],
                                parent_group=[SystemGroup.CHAT_USER]
                                )
    CHAT_USER_DELETE = Permission(group=Group.CHAT_USER, operate=Operate.DELETE,
                                  role_list=[RoleConstants.ADMIN],
                                  parent_group=[SystemGroup.CHAT_USER]
                                  )
    CHAT_USER_GROUP = Permission(group=Group.CHAT_USER, operate=Operate.USER_GROUP,
                                 role_list=[RoleConstants.ADMIN],
                                 parent_group=[SystemGroup.CHAT_USER],
                                 label=_('Set up user groups')
                                 )
    USER_GROUP_READ = Permission(group=Group.USER_GROUP, operate=Operate.READ,
                                 role_list=[RoleConstants.ADMIN],
                                 parent_group=[SystemGroup.CHAT_USER]
                                 )
    USER_GROUP_CREATE = Permission(group=Group.USER_GROUP, operate=Operate.CREATE,
                                   role_list=[RoleConstants.ADMIN],
                                   parent_group=[SystemGroup.CHAT_USER]
                                   )
    USER_GROUP_EDIT = Permission(group=Group.USER_GROUP, operate=Operate.EDIT,
                                 role_list=[RoleConstants.ADMIN],
                                 parent_group=[SystemGroup.CHAT_USER]
                                 )
    USER_GROUP_DELETE = Permission(group=Group.USER_GROUP, operate=Operate.DELETE,
                                   role_list=[RoleConstants.ADMIN],
                                   parent_group=[SystemGroup.CHAT_USER]
                                   )
    USER_GROUP_ADD_MEMBER = Permission(group=Group.USER_GROUP, operate=Operate.ADD_MEMBER,
                                       role_list=[RoleConstants.ADMIN],
                                       parent_group=[SystemGroup.CHAT_USER]
                                       )
    USER_GROUP_REMOVE_MEMBER = Permission(group=Group.USER_GROUP, operate=Operate.REMOVE_MEMBER,
                                          role_list=[RoleConstants.ADMIN],
                                          parent_group=[SystemGroup.CHAT_USER]
                                          )
    CHAT_USER_AUTH_READ = Permission(group=Group.CHAT_USER_AUTH, operate=Operate.READ,
                                     role_list=[RoleConstants.ADMIN],
                                     parent_group=[SystemGroup.CHAT_USER]
                                     )
    CHAT_USER_AUTH_EDIT = Permission(group=Group.CHAT_USER_AUTH, operate=Operate.EDIT,
                                     role_list=[RoleConstants.ADMIN],
                                     parent_group=[SystemGroup.CHAT_USER]
                                     )
    WORKSPACE_CHAT_USER_READ = Permission(group=Group.WORKSPACE_CHAT_USER, operate=Operate.READ,
                                          role_list=[RoleConstants.ADMIN],
                                          parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
                                          )
    WORKSPACE_CHAT_USER_CREATE = Permission(group=Group.WORKSPACE_CHAT_USER, operate=Operate.CREATE,
                                            role_list=[RoleConstants.ADMIN],
                                            parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
                                            )
    WORKSPACE_CHAT_USER_EDIT = Permission(group=Group.WORKSPACE_CHAT_USER, operate=Operate.EDIT,
                                          role_list=[RoleConstants.ADMIN],
                                          parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
                                          )
    WORKSPACE_CHAT_USER_DELETE = Permission(group=Group.WORKSPACE_CHAT_USER, operate=Operate.DELETE,
                                            role_list=[RoleConstants.ADMIN],
                                            parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
                                            )
    WORKSPACE_CHAT_USER_GROUP = Permission(group=Group.WORKSPACE_CHAT_USER, operate=Operate.USER_GROUP,
                                           role_list=[RoleConstants.ADMIN],
                                           parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT],
                                           label=_('Set up user groups')
                                           )
    WORKSPACE_USER_GROUP_READ = Permission(group=Group.WORKSPACE_USER_GROUP, operate=Operate.READ,
                                           role_list=[RoleConstants.ADMIN],
                                           parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
                                           )
    WORKSPACE_USER_GROUP_CREATE = Permission(group=Group.WORKSPACE_USER_GROUP, operate=Operate.CREATE,
                                             role_list=[RoleConstants.ADMIN],
                                             parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
                                             )
    WORKSPACE_USER_GROUP_EDIT = Permission(group=Group.WORKSPACE_USER_GROUP, operate=Operate.EDIT,
                                           role_list=[RoleConstants.ADMIN],
                                           parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
                                           )
    WORKSPACE_USER_GROUP_DELETE = Permission(group=Group.WORKSPACE_USER_GROUP, operate=Operate.DELETE,
                                             role_list=[RoleConstants.ADMIN],
                                             parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
                                             )
    WORKSPACE_USER_GROUP_ADD_MEMBER = Permission(group=Group.WORKSPACE_USER_GROUP, operate=Operate.ADD_MEMBER,
                                                 role_list=[RoleConstants.ADMIN],
                                                 parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
                                                 )
    WORKSPACE_USER_GROUP_REMOVE_MEMBER = Permission(group=Group.WORKSPACE_USER_GROUP, operate=Operate.REMOVE_MEMBER,
                                                    role_list=[RoleConstants.ADMIN],
                                                    parent_group=[WorkspaceGroup.SYSTEM_MANAGEMENT]
                                                    )

    SHARED_TOOL_READ = Permission(group=Group.SYSTEM_TOOL, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
                                  parent_group=[SystemGroup.SHARED_TOOL], is_ee=settings.edition == "EE"
                                  )

    SHARED_TOOL_CREATE = Permission(group=Group.SYSTEM_TOOL, operate=Operate.CREATE, role_list=[RoleConstants.ADMIN],
                                    parent_group=[SystemGroup.SHARED_TOOL], is_ee=settings.edition == "EE"
                                    )

    SHARED_TOOL_EDIT = Permission(
        group=Group.SYSTEM_TOOL, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_TOOL], is_ee=settings.edition == "EE"
    )

    SHARED_TOOL_DELETE = Permission(
        group=Group.SYSTEM_TOOL, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_TOOL], is_ee=settings.edition == "EE"
    )
    SHARED_TOOL_IMPORT = Permission(
        group=Group.SYSTEM_TOOL, operate=Operate.IMPORT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_TOOL], is_ee=settings.edition == "EE"
    )
    SHARED_TOOL_EXPORT = Permission(
        group=Group.SYSTEM_TOOL, operate=Operate.EXPORT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_TOOL], is_ee=settings.edition == "EE"
    )
    SHARED_TOOL_DEBUG = Permission(
        group=Group.SYSTEM_TOOL, operate=Operate.DEBUG, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_TOOL], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_READ = Permission(
        group=Group.SYSTEM_KNOWLEDGE, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_CREATE = Permission(
        group=Group.SYSTEM_KNOWLEDGE, operate=Operate.CREATE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_EDIT = Permission(
        group=Group.SYSTEM_KNOWLEDGE, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_SYNC = Permission(
        group=Group.SYSTEM_KNOWLEDGE, operate=Operate.SYNC, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_VECTOR = Permission(
        group=Group.SYSTEM_KNOWLEDGE, operate=Operate.VECTOR, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_EXPORT = Permission(
        group=Group.SYSTEM_KNOWLEDGE, operate=Operate.EXPORT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_GENERATE = Permission(
        group=Group.SYSTEM_KNOWLEDGE, operate=Operate.GENERATE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_DELETE = Permission(
        group=Group.SYSTEM_KNOWLEDGE, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_DOCUMENT_READ = Permission(
        group=Group.SYSTEM_KNOWLEDGE_DOCUMENT, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_DOCUMENT_CREATE = Permission(
        group=Group.SYSTEM_KNOWLEDGE_DOCUMENT, operate=Operate.CREATE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_DOCUMENT_EDIT = Permission(
        group=Group.SYSTEM_KNOWLEDGE_DOCUMENT, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_DOCUMENT_DELETE = Permission(
        group=Group.SYSTEM_KNOWLEDGE_DOCUMENT, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_DOCUMENT_SYNC = Permission(
        group=Group.SYSTEM_KNOWLEDGE_DOCUMENT, operate=Operate.SYNC, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_DOCUMENT_EXPORT = Permission(
        group=Group.SYSTEM_KNOWLEDGE_DOCUMENT, operate=Operate.EXPORT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE = Permission(
        group=Group.SYSTEM_KNOWLEDGE_DOCUMENT, operate=Operate.DOWNLOAD, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_DOCUMENT_GENERATE = Permission(
        group=Group.SYSTEM_KNOWLEDGE_DOCUMENT, operate=Operate.GENERATE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_DOCUMENT_VECTOR = Permission(
        group=Group.SYSTEM_KNOWLEDGE_DOCUMENT, operate=Operate.VECTOR, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_DOCUMENT_MIGRATE = Permission(
        group=Group.SYSTEM_KNOWLEDGE_DOCUMENT, operate=Operate.MIGRATE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_PROBLEM_READ = Permission(
        group=Group.SYSTEM_KNOWLEDGE_PROBLEM, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_PROBLEM_CREATE = Permission(
        group=Group.SYSTEM_KNOWLEDGE_PROBLEM, operate=Operate.CREATE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_PROBLEM_EDIT = Permission(
        group=Group.SYSTEM_KNOWLEDGE_PROBLEM, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_PROBLEM_DELETE = Permission(
        group=Group.SYSTEM_KNOWLEDGE_PROBLEM, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_PROBLEM_RELATE = Permission(
        group=Group.SYSTEM_KNOWLEDGE_PROBLEM, operate=Operate.RELATE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_HIT_TEST = Permission(
        group=Group.SYSTEM_KNOWLEDGE_HIT_TEST, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_CHAT_USER_READ = Permission(
        group=Group.SYSTEM_KNOWLEDGE_CHAT_USER, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_KNOWLEDGE_CHAT_USER_EDIT = Permission(
        group=Group.SYSTEM_KNOWLEDGE_CHAT_USER, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.SHARED_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    SHARED_MODEL_READ = Permission(
        group=Group.SYSTEM_MODEL, operate=Operate.READ, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[SystemGroup.SHARED_MODEL], is_ee=settings.edition == "EE"
    )
    SHARED_MODEL_CREATE = Permission(
        group=Group.SYSTEM_MODEL, operate=Operate.CREATE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[SystemGroup.SHARED_MODEL], is_ee=settings.edition == "EE"
    )

    SHARED_MODEL_EDIT = Permission(
        group=Group.SYSTEM_MODEL, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[SystemGroup.SHARED_MODEL], is_ee=settings.edition == "EE"
    )
    SHARED_MODEL_DELETE = Permission(
        group=Group.SYSTEM_MODEL, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN, RoleConstants.USER],
        parent_group=[SystemGroup.SHARED_MODEL], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_READ = Permission(
        group=Group.SYSTEM_RES_APPLICATION, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_DEBUG = Permission(
        group=Group.SYSTEM_RES_APPLICATION, operate=Operate.DEBUG, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_EXPORT = Permission(
        group=Group.SYSTEM_RES_APPLICATION, operate=Operate.EXPORT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_DELETE = Permission(
        group=Group.SYSTEM_RES_APPLICATION, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_EDIT = Permission(
        group=Group.SYSTEM_RES_APPLICATION, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_AUTH = Permission(
        group=Group.SYSTEM_RES_APPLICATION, operate=Operate.AUTH, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_OVERVIEW_READ = Permission(
        group=Group.SYSTEM_RES_APPLICATION_OVERVIEW, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_OVERVIEW_EMBED = Permission(
        group=Group.SYSTEM_RES_APPLICATION_OVERVIEW, operate=Operate.EMBED, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_OVERVIEW_ACCESS = Permission(
        group=Group.SYSTEM_RES_APPLICATION_OVERVIEW, operate=Operate.ACCESS, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_OVERVIEW_DISPLAY = Permission(
        group=Group.SYSTEM_RES_APPLICATION_OVERVIEW, operate=Operate.DISPLAY, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_OVERVIEW_API_KEY = Permission(
        group=Group.SYSTEM_RES_APPLICATION_OVERVIEW, operate=Operate.API_KEY, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_OVERVIEW_PUBLIC = Permission(
        group=Group.SYSTEM_RES_APPLICATION_OVERVIEW, operate=Operate.PUBLIC_ACCESS, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    # 应用接入
    RESOURCE_APPLICATION_ACCESS_READ = Permission(
        group=Group.SYSTEM_RES_APPLICATION_ACCESS, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_ACCESS_EDIT = Permission(
        group=Group.SYSTEM_RES_APPLICATION_ACCESS, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_CHAT_USER_READ = Permission(
        group=Group.SYSTEM_RES_APPLICATION_CHAT_USER, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_CHAT_USER_EDIT = Permission(
        group=Group.SYSTEM_RES_APPLICATION_CHAT_USER, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_CHAT_LOG_READ = Permission(
        group=Group.SYSTEM_RES_APPLICATION_CHAT_LOG, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_CHAT_LOG_ADD_KNOWLEDGE = Permission(
        group=Group.SYSTEM_RES_APPLICATION_CHAT_LOG, operate=Operate.ADD_KNOWLEDGE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_CHAT_LOG_ANNOTATION = Permission(
        group=Group.SYSTEM_RES_APPLICATION_CHAT_LOG, operate=Operate.ANNOTATION, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_CHAT_LOG_EXPORT = Permission(
        group=Group.SYSTEM_RES_APPLICATION_CHAT_LOG, operate=Operate.EXPORT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    RESOURCE_APPLICATION_CHAT_LOG_CLEAR_POLICY = Permission(
        group=Group.SYSTEM_RES_APPLICATION_CHAT_LOG, operate=Operate.CLEAR_POLICY, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_APPLICATION], is_ee=settings.edition == "EE"
    )
    # 知识库
    RESOURCE_KNOWLEDGE_READ = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_EDIT = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_DELETE = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_SYNC = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.SYNC, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_EXPORT = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.EXPORT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_VECTOR = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.VECTOR, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_GENERATE = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.GENERATE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_AUTH = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.AUTH, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    # 文档
    RESOURCE_KNOWLEDGE_DOCUMENT_READ = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_DOCUMENT, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_DOCUMENT_CREATE = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_DOCUMENT, operate=Operate.CREATE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_DOCUMENT_EDIT = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_DOCUMENT, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_DOCUMENT_DELETE = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_DOCUMENT, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_DOCUMENT_SYNC = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_DOCUMENT, operate=Operate.SYNC, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_DOCUMENT_EXPORT = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_DOCUMENT, operate=Operate.EXPORT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_DOCUMENT, operate=Operate.DOWNLOAD, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_DOCUMENT_GENERATE = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_DOCUMENT, operate=Operate.GENERATE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_DOCUMENT_VECTOR = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_DOCUMENT, operate=Operate.VECTOR, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_DOCUMENT_MIGRATE = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_DOCUMENT, operate=Operate.MIGRATE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_HIT_TEST = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_HIT_TEST, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_PROBLEM_READ = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_PROBLEM, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_PROBLEM_CREATE = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_PROBLEM, operate=Operate.CREATE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_PROBLEM_EDIT = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_PROBLEM, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_PROBLEM_DELETE = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_PROBLEM, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_PROBLEM_RELATE = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_PROBLEM, operate=Operate.RELATE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_CHAT_USER_READ = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_CHAT_USER, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_KNOWLEDGE_CHAT_USER_EDIT = Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE_CHAT_USER, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_KNOWLEDGE], is_ee=settings.edition == "EE"
    )
    RESOURCE_TOOL_READ = Permission(
        group=Group.SYSTEM_RES_TOOL, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_TOOL], is_ee=settings.edition == "EE"
    )
    RESOURCE_TOOL_EDIT = Permission(
        group=Group.SYSTEM_RES_TOOL, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_TOOL], is_ee=settings.edition == "EE"
    )
    RESOURCE_TOOL_DELETE = Permission(
        group=Group.SYSTEM_RES_TOOL, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_TOOL], is_ee=settings.edition == "EE"
    )
    RESOURCE_TOOL_DEBUG = Permission(
        group=Group.SYSTEM_RES_TOOL, operate=Operate.DEBUG, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_TOOL], is_ee=settings.edition == "EE"
    )
    RESOURCE_TOOL_EXPORT = Permission(
        group=Group.SYSTEM_RES_TOOL, operate=Operate.EXPORT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_TOOL], is_ee=settings.edition == "EE"
    )
    RESOURCE_TOOL_AUTH = Permission(
        group=Group.SYSTEM_RES_TOOL, operate=Operate.AUTH, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_TOOL], is_ee=settings.edition == "EE"
    )
    RESOURCE_MODEL_READ = Permission(
        group=Group.SYSTEM_RES_MODEL, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_MODEL], is_ee=settings.edition == "EE"
    )
    RESOURCE_MODEL_EDIT = Permission(
        group=Group.SYSTEM_RES_MODEL, operate=Operate.EDIT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_MODEL], is_ee=settings.edition == "EE"
    )
    RESOURCE_MODEL_DELETE = Permission(
        group=Group.SYSTEM_RES_MODEL, operate=Operate.DELETE, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_MODEL], is_ee=settings.edition == "EE"
    )
    RESOURCE_MODEL_AUTH = Permission(
        group=Group.SYSTEM_RES_MODEL, operate=Operate.AUTH, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.RESOURCE_MODEL], is_ee=settings.edition == "EE"
    )
    OPERATION_LOG_READ = Permission(
        group=Group.OPERATION_LOG, operate=Operate.READ, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.OPERATION_LOG]
    )
    OPERATION_LOG_EXPORT = Permission(
        group=Group.OPERATION_LOG, operate=Operate.EXPORT, role_list=[RoleConstants.ADMIN],
        parent_group=[SystemGroup.OPERATION_LOG]
    )

    def get_workspace_application_permission(self):
        return lambda r, kwargs: Permission(group=self.value.group, operate=self.value.operate,
                                            resource_path=
                                            f"/WORKSPACE/{kwargs.get('workspace_id')}/APPLICATION/{kwargs.get('application_id')}")

    def get_workspace_knowledge_permission(self):
        return lambda r, kwargs: Permission(group=self.value.group, operate=self.value.operate,
                                            resource_path=
                                            f"/WORKSPACE/{kwargs.get('workspace_id')}/KNOWLEDGE/{kwargs.get('knowledge_id')}")

    def get_workspace_model_permission(self):
        return lambda r, kwargs: Permission(group=self.value.group, operate=self.value.operate,
                                            resource_path=
                                            f"/WORKSPACE/{kwargs.get('workspace_id')}/MODEL/{kwargs.get('model_id')}")

    def get_workspace_tool_permission(self):
        return lambda r, kwargs: Permission(group=self.value.group, operate=self.value.operate,
                                            resource_path=
                                            f"/WORKSPACE/{kwargs.get('workspace_id')}/TOOL/{kwargs.get('tool_id')}")

    def get_workspace_permission(self):
        return lambda r, kwargs: Permission(group=self.value.group, operate=self.value.operate,
                                            resource_path=
                                            f"/WORKSPACE/{kwargs.get('workspace_id')}")

    def get_workspace_permission_workspace_manage_role(self):
        return lambda r, kwargs: Permission(group=self.value.group, operate=self.value.operate,
                                            resource_path=
                                            f"/WORKSPACE/{kwargs.get('workspace_id')}:ROLE/{RoleConstants.WORKSPACE_MANAGE.value.__str__()}")

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
    return [PermissionConstants[k].value for k in PermissionConstants.__members__ if
            PermissionConstants[k].value.resource_permission_group_list.__contains__(resource_group)]


class ChatAuth:
    def __init__(self,
                 current_role_list: List[RoleConstants | Role],
                 permission_list: List[PermissionConstants | Permission],
                 chat_user_id,
                 chat_user_type,
                 application_id):
        # 权限列表
        self.permission_list = permission_list
        # 角色列表
        self.role_list = current_role_list
        self.chat_user_id = chat_user_id
        self.chat_user_type = chat_user_type
        self.application_id = application_id


class Auth:
    """
     用于存储当前用户的角色和权限
    """

    def __init__(self,
                 current_role_list: List[RoleConstants | Role],
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
