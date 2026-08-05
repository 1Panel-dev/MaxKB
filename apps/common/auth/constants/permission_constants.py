# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： permission_constants.py
    @date：2026/8/3 17:28
    @desc: 权限枚举常量（新格式）
"""
from enum import Enum
from typing import List, Dict

from common.auth.constants.category_constants import Category
from common.auth.constants.group_constants import Group
from common.auth.constants.operate_constants import Operate
from common.auth.constants.permission_scope_constants import PermissionScopeConstants
from common.auth.constants.role_constants import RoleConstants
from common.auth.struct.permission import Permission, PermissionMeta


class ResourcePermissionGroup:
    """资源权限组"""

    def __init__(self, resource: Group, permission: str):
        self.resource = resource
        self.permission = permission

    def __eq__(self, other):
        return str(self.permission) == str(other.permission) and str(self.resource) == str(other.resource)

    def __str__(self):
        return f"{self.resource}_{self.permission}"

    def __hash__(self):
        return hash((self.resource, self.permission))


class ResourcePermissionConst:
    """资源权限常量"""
    # 知识库
    KNOWLEDGE_VIEW = ResourcePermissionGroup(Group.KNOWLEDGE, "VIEW")
    KNOWLEDGE_MANAGE = ResourcePermissionGroup(Group.KNOWLEDGE, "MANAGE")
    KNOWLEDGE_FOLDER_VIEW = ResourcePermissionGroup(Group.KNOWLEDGE, "FOLDER_VIEW")
    KNOWLEDGE_FOLDER_MANAGE = ResourcePermissionGroup(Group.KNOWLEDGE, "FOLDER_MANAGE")

    # 应用
    APPLICATION_VIEW = ResourcePermissionGroup(Group.APPLICATION, "VIEW")
    APPLICATION_MANAGE = ResourcePermissionGroup(Group.APPLICATION, "MANAGE")
    APPLICATION_FOLDER_VIEW = ResourcePermissionGroup(Group.APPLICATION, "FOLDER_VIEW")
    APPLICATION_FOLDER_MANAGE = ResourcePermissionGroup(Group.APPLICATION, "FOLDER_MANAGE")

    # 工具
    TOOL_VIEW = ResourcePermissionGroup(Group.TOOL, "VIEW")
    TOOL_MANAGE = ResourcePermissionGroup(Group.TOOL, "MANAGE")
    TOOL_FOLDER_VIEW = ResourcePermissionGroup(Group.TOOL, "FOLDER_VIEW")
    TOOL_FOLDER_MANAGE = ResourcePermissionGroup(Group.TOOL, "FOLDER_MANAGE")

    # 模型
    MODEL_VIEW = ResourcePermissionGroup(Group.MODEL, "VIEW")
    MODEL_MANAGE = ResourcePermissionGroup(Group.MODEL, "MANAGE")


class PermissionConstants(Enum):
    """
     权限枚举
    """
    # ==================== 首页 ====================
    HOMEPAGE_READ = (Permission(
        group=Group.HOMEPAGE, sub_group=Group.HOMEPAGE, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.WORKSPACE))

    HOMEPAGE_EXPORT = (Permission(
        group=Group.HOMEPAGE, sub_group=Group.HOMEPAGE, operate=Operate.EXPORT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.WORKSPACE))

    # ==================== 资源主分组（无子分组） ====================
    KNOWLEDGE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.KNOWLEDGE, operate=Operate.SELF, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE))

    APPLICATION = (Permission(
        group=Group.APPLICATION, sub_group=Group.APPLICATION, operate=Operate.SELF, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE))

    MODEL = (Permission(
        group=Group.MODEL, sub_group=Group.MODEL, operate=Operate.SELF, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE))

    TOOL = (Permission(
        group=Group.TOOL, sub_group=Group.TOOL, operate=Operate.SELF, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE))

    # ==================== 用户管理 ====================
    USER_READ = (Permission(
        group=Group.USER, sub_group=Group.USER, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.IAM))

    USER_CREATE = (Permission(
        group=Group.USER, sub_group=Group.USER, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    USER_EDIT = (Permission(
        group=Group.USER, sub_group=Group.USER, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    USER_DELETE = (Permission(
        group=Group.USER, sub_group=Group.USER, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    USER_SET_ROLE = (Permission(
        group=Group.USER, sub_group=Group.USER, operate=Operate.SET_ROLE, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM, is_ee=True))

    USER_IMPORT = (Permission(
        group=Group.USER, sub_group=Group.USER, operate=Operate.IMPORT, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    # ==================== 系统用户组 ====================
    SYSTEM_USER_GROUP_READ = (Permission(
        group=Group.USER_GROUP, sub_group=Group.USER_GROUP, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE], category=Category.IAM))

    SYSTEM_USER_GROUP_CREATE = (Permission(
        group=Group.USER_GROUP, sub_group=Group.USER_GROUP, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE], category=Category.IAM))

    SYSTEM_USER_GROUP_EDIT = (Permission(
        group=Group.USER_GROUP, sub_group=Group.USER_GROUP, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE], category=Category.IAM))

    SYSTEM_USER_GROUP_DELETE = (Permission(
        group=Group.USER_GROUP, sub_group=Group.USER_GROUP, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE], category=Category.IAM))

    SYSTEM_USER_GROUP_ADD_MEMBER = (Permission(
        group=Group.USER_GROUP, sub_group=Group.USER_GROUP, operate=Operate.ADD_MEMBER, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE], category=Category.IAM))

    SYSTEM_USER_GROUP_REMOVE_MEMBER = (Permission(
        group=Group.USER_GROUP, sub_group=Group.USER_GROUP, operate=Operate.REMOVE_MEMBER, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE], category=Category.IAM))

    # ==================== 模型 ====================
    MODEL_READ = (Permission(
        group=Group.MODEL, sub_group=Group.MODEL, operate=Operate.READ, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.MODEL_VIEW]))

    MODEL_CREATE = (Permission(
        group=Group.MODEL, sub_group=Group.MODEL, operate=Operate.CREATE, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.MODEL_MANAGE]))

    MODEL_EDIT = (Permission(
        group=Group.MODEL, sub_group=Group.MODEL, operate=Operate.EDIT, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.MODEL_MANAGE]))

    MODEL_DELETE = (Permission(
        group=Group.MODEL, sub_group=Group.MODEL, operate=Operate.DELETE, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.MODEL_MANAGE]))

    MODEL_RESOURCE_AUTHORIZATION = (Permission(
        group=Group.MODEL, sub_group=Group.MODEL, operate=Operate.AUTH, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.MODEL_MANAGE]))

    MODEL_RELATE_RESOURCE_VIEW = (Permission(
        group=Group.MODEL, sub_group=Group.MODEL, operate=Operate.RELATE_VIEW, bit_index=6
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.MODEL_MANAGE]))

    # ==================== 触发器 ====================
    TRIGGER_READ = (Permission(
        group=Group.TRIGGER, sub_group=Group.TRIGGER, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.WORKSPACE))

    TRIGGER_CREATE = (Permission(
        group=Group.TRIGGER, sub_group=Group.TRIGGER, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.WORKSPACE))

    TRIGGER_EDIT = (Permission(
        group=Group.TRIGGER, sub_group=Group.TRIGGER, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.WORKSPACE))

    TRIGGER_DELETE = (Permission(
        group=Group.TRIGGER, sub_group=Group.TRIGGER, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.WORKSPACE))

    TRIGGER_RECORD = (Permission(
        group=Group.TRIGGER, sub_group=Group.TRIGGER, operate=Operate.RECORD, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.WORKSPACE))

    # ==================== 工具 ====================
    TOOL_READ = (Permission(
        group=Group.TOOL, sub_group=Group.TOOL, operate=Operate.READ, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_VIEW]))

    TOOL_CREATE = (Permission(
        group=Group.TOOL, sub_group=Group.TOOL, operate=Operate.CREATE, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_MANAGE]))

    TOOL_BATCH_MOVE = (Permission(
        group=Group.TOOL, sub_group=Group.TOOL, operate=Operate.BATCH_MOVE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_MANAGE]))

    TOOL_BATCH_DELETE = (Permission(
        group=Group.TOOL, sub_group=Group.TOOL, operate=Operate.BATCH_DELETE, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_MANAGE]))

    TOOL_EDIT = (Permission(
        group=Group.TOOL, sub_group=Group.TOOL, operate=Operate.EDIT, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_MANAGE]))

    TOOL_DELETE = (Permission(
        group=Group.TOOL, sub_group=Group.TOOL, operate=Operate.DELETE, bit_index=6
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_MANAGE]))

    TOOL_IMPORT = (Permission(
        group=Group.TOOL, sub_group=Group.TOOL, operate=Operate.IMPORT, bit_index=7
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_MANAGE]))

    TOOL_EXPORT = (Permission(
        group=Group.TOOL, sub_group=Group.TOOL, operate=Operate.EXPORT, bit_index=8
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_MANAGE]))

    TOOL_RESOURCE_AUTHORIZATION = (Permission(
        group=Group.TOOL, sub_group=Group.TOOL, operate=Operate.AUTH, bit_index=9
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_MANAGE]))

    TOOL_RELATE_RESOURCE_VIEW = (Permission(
        group=Group.TOOL, sub_group=Group.TOOL, operate=Operate.RELATE_VIEW, bit_index=10
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_MANAGE]))

    TOOL_PUBLISH = (Permission(
        group=Group.TOOL, sub_group=Group.TOOL, operate=Operate.PUBLISH, bit_index=11
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_MANAGE]))

    TOOL_EXECUTE_RECORD = (Permission(
        group=Group.TOOL, sub_group=Group.TOOL, operate=Operate.RECORD, bit_index=12
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_MANAGE]))

    # 工具触发器
    TOOL_TRIGGER_READ = (Permission(
        group=Group.TOOL, sub_group=Group.TOOL, operate=Operate.TRIGGER_READ, bit_index=13
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_MANAGE]))

    TOOL_TRIGGER_CREATE = (Permission(
        group=Group.TOOL, sub_group=Group.TOOL, operate=Operate.TRIGGER_CREATE, bit_index=14
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_VIEW]))

    TOOL_TRIGGER_EDIT = (Permission(
        group=Group.TOOL, sub_group=Group.TOOL, operate=Operate.TRIGGER_EDIT, bit_index=15
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_VIEW]))

    TOOL_TRIGGER_DELETE = (Permission(
        group=Group.TOOL, sub_group=Group.TOOL, operate=Operate.TRIGGER_DELETE, bit_index=16
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_VIEW]))

    # ==================== 工具文件夹 ====================
    TOOL_FOLDER_READ = (Permission(
        group=Group.TOOL, sub_group=Group.FOLDER, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_VIEW]))

    TOOL_FOLDER_CREATE = (Permission(
        group=Group.TOOL, sub_group=Group.FOLDER, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_MANAGE]))

    TOOL_FOLDER_EDIT = (Permission(
        group=Group.TOOL, sub_group=Group.FOLDER, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_MANAGE]))

    TOOL_FOLDER_DELETE = (Permission(
        group=Group.TOOL, sub_group=Group.FOLDER, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_MANAGE]))

    TOOL_FOLDER_AUTH = (Permission(
        group=Group.TOOL, sub_group=Group.FOLDER, operate=Operate.AUTH, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.TOOL_MANAGE]))

    # ==================== 知识库 ====================
    KNOWLEDGE_READ = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.KNOWLEDGE, operate=Operate.READ, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_VIEW]))

    KNOWLEDGE_CREATE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.KNOWLEDGE, operate=Operate.CREATE, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_VIEW]))

    KNOWLEDGE_EDIT = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.KNOWLEDGE, operate=Operate.EDIT, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_DELETE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.KNOWLEDGE, operate=Operate.DELETE, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_SYNC = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.KNOWLEDGE, operate=Operate.SYNC, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_EXPORT = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.KNOWLEDGE, operate=Operate.EXPORT, bit_index=6
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_VECTOR = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.KNOWLEDGE, operate=Operate.VECTOR, bit_index=7
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_GENERATE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.KNOWLEDGE, operate=Operate.GENERATE, bit_index=8
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_BATCH_DELETE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.KNOWLEDGE, operate=Operate.BATCH_DELETE, bit_index=9
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_BATCH_MOVE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.KNOWLEDGE, operate=Operate.BATCH_MOVE, bit_index=10
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_RESOURCE_AUTHORIZATION = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.KNOWLEDGE, operate=Operate.AUTH, bit_index=11
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_RELATE_RESOURCE_VIEW = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.KNOWLEDGE, operate=Operate.RELATE_VIEW, bit_index=12
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    # ==================== 知识库文件夹 ====================
    KNOWLEDGE_FOLDER_READ = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.FOLDER, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_VIEW]))

    KNOWLEDGE_FOLDER_CREATE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.FOLDER, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_FOLDER_EDIT = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.FOLDER, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_FOLDER_DELETE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.FOLDER, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_FOLDER_AUTH = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.FOLDER, operate=Operate.AUTH, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    # ==================== 知识库工作流 ====================
    KNOWLEDGE_WORKFLOW_READ = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.WORKFLOW, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_VIEW]))

    KNOWLEDGE_WORKFLOW_EDIT = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.WORKFLOW, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_WORKFLOW_EXPORT = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.WORKFLOW, operate=Operate.EXPORT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_WORKFLOW_PUBLISH = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.WORKFLOW, operate=Operate.PUBLISH, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    # ==================== 知识库文档 ====================
    KNOWLEDGE_DOCUMENT_READ = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.DOCUMENT, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_VIEW]))

    KNOWLEDGE_DOCUMENT_CREATE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.DOCUMENT, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_DOCUMENT_EDIT = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.DOCUMENT, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_DOCUMENT_DELETE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.DOCUMENT, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_DOCUMENT_SYNC = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.DOCUMENT, operate=Operate.SYNC, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_DOCUMENT_EXPORT = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.DOCUMENT, operate=Operate.EXPORT, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.DOCUMENT, operate=Operate.DOWNLOAD, bit_index=6
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_DOCUMENT_GENERATE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.DOCUMENT, operate=Operate.GENERATE, bit_index=7
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_DOCUMENT_VECTOR = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.DOCUMENT, operate=Operate.VECTOR, bit_index=8
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_DOCUMENT_MIGRATE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.DOCUMENT, operate=Operate.MIGRATE, bit_index=9
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_DOCUMENT_TAG = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.DOCUMENT, operate=Operate.TAG, bit_index=10
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_DOCUMENT_REPLACE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.DOCUMENT, operate=Operate.REPLACE, bit_index=11
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_DOCUMENT_TOKEN = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.DOCUMENT, operate=Operate.TOKEN, bit_index=12
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_VIEW]))

    # ==================== 知识库命中测试 ====================
    KNOWLEDGE_HIT_TEST = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.HIT_TEST, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_VIEW]))

    # ==================== 知识库问题 ====================
    KNOWLEDGE_PROBLEM_READ = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.PROBLEM, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_VIEW]))

    KNOWLEDGE_PROBLEM_CREATE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.PROBLEM, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_PROBLEM_EDIT = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.PROBLEM, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_PROBLEM_DELETE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.PROBLEM, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_PROBLEM_RELATE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.PROBLEM, operate=Operate.RELATE, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    # ==================== 知识库术语库 ====================
    KNOWLEDGE_TERMBASE_READ = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.TERMBASE, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_VIEW]))

    KNOWLEDGE_TERMBASE_CREATE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.TERMBASE, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_TERMBASE_EDIT = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.TERMBASE, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_TERMBASE_DELETE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.TERMBASE, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    # ==================== 知识库标签 ====================
    KNOWLEDGE_TAG_READ = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.TAG, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_TAG_CREATE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.TAG, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_TAG_EDIT = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.TAG, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    KNOWLEDGE_TAG_DELETE = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.TAG, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    # ==================== 知识库对话用户 ====================
    KNOWLEDGE_CHAT_USER_READ = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.CHAT_USER, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_VIEW]))

    KNOWLEDGE_CHAT_USER_EDIT = (Permission(
        group=Group.KNOWLEDGE, sub_group=Group.CHAT_USER, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.KNOWLEDGE_MANAGE]))

    # ==================== 资源授权 ====================
    APPLICATION_WORKSPACE_USER_RESOURCE_PERMISSION_READ = (Permission(
        group=Group.RESOURCE_PERMISSION, sub_group=Group.RESOURCE_PERMISSION, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE], category=Category.IAM))

    APPLICATION_WORKSPACE_USER_RESOURCE_PERMISSION_EDIT = (Permission(
        group=Group.RESOURCE_PERMISSION, sub_group=Group.RESOURCE_PERMISSION, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE], category=Category.IAM))

    KNOWLEDGE_WORKSPACE_USER_RESOURCE_PERMISSION_READ = (Permission(
        group=Group.RESOURCE_PERMISSION, sub_group=Group.RESOURCE_PERMISSION, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE], category=Category.IAM))

    KNOWLEDGE_WORKSPACE_USER_RESOURCE_PERMISSION_EDIT = (Permission(
        group=Group.RESOURCE_PERMISSION, sub_group=Group.RESOURCE_PERMISSION, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE], category=Category.IAM))

    TOOL_WORKSPACE_USER_RESOURCE_PERMISSION_READ = (Permission(
        group=Group.RESOURCE_PERMISSION, sub_group=Group.RESOURCE_PERMISSION, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE], category=Category.IAM))

    TOOL_WORKSPACE_USER_RESOURCE_PERMISSION_EDIT = (Permission(
        group=Group.RESOURCE_PERMISSION, sub_group=Group.RESOURCE_PERMISSION, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE], category=Category.IAM))

    MODEL_WORKSPACE_USER_RESOURCE_PERMISSION_READ = (Permission(
        group=Group.RESOURCE_PERMISSION, sub_group=Group.RESOURCE_PERMISSION, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE], category=Category.IAM))

    MODEL_WORKSPACE_USER_RESOURCE_PERMISSION_EDIT = (Permission(
        group=Group.RESOURCE_PERMISSION, sub_group=Group.RESOURCE_PERMISSION, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE], category=Category.IAM))

    # ==================== 邮件设置 ====================
    EMAIL_SETTING_READ = (Permission(
        group=Group.EMAIL_SETTING, sub_group=Group.EMAIL_SETTING, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SYSTEM_SETTING))

    EMAIL_SETTING_EDIT = (Permission(
        group=Group.EMAIL_SETTING, sub_group=Group.EMAIL_SETTING, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SYSTEM_SETTING))

    # ==================== 角色管理 ====================
    ROLE_READ = (Permission(
        group=Group.ROLE, sub_group=Group.ROLE, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.IAM))

    ROLE_CREATE = (Permission(
        group=Group.ROLE, sub_group=Group.ROLE, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    ROLE_EDIT = (Permission(
        group=Group.ROLE, sub_group=Group.ROLE, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    ROLE_DELETE = (Permission(
        group=Group.ROLE, sub_group=Group.ROLE, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    ROLE_ADD_MEMBER = (Permission(
        group=Group.ROLE, sub_group=Group.ROLE, operate=Operate.ADD_MEMBER, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    ROLE_REMOVE_MEMBER = (Permission(
        group=Group.ROLE, sub_group=Group.ROLE, operate=Operate.REMOVE_MEMBER, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    # ==================== 工作空间角色管理 ====================
    WORKSPACE_ROLE_READ = (Permission(
        group=Group.WORKSPACE_ROLE, sub_group=Group.WORKSPACE_ROLE, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    WORKSPACE_ROLE_ADD_MEMBER = (Permission(
        group=Group.WORKSPACE_ROLE, sub_group=Group.WORKSPACE_ROLE, operate=Operate.ADD_MEMBER, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    WORKSPACE_ROLE_REMOVE_MEMBER = (Permission(
        group=Group.WORKSPACE_ROLE, sub_group=Group.WORKSPACE_ROLE, operate=Operate.REMOVE_MEMBER, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    # ==================== 工作空间管理 ====================
    WORKSPACE_READ = (Permission(
        group=Group.WORKSPACE, sub_group=Group.WORKSPACE, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.IAM, is_ee=True))

    WORKSPACE_CREATE = (Permission(
        group=Group.WORKSPACE, sub_group=Group.WORKSPACE, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM, is_ee=True))

    WORKSPACE_EDIT = (Permission(
        group=Group.WORKSPACE, sub_group=Group.WORKSPACE, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM, is_ee=True))

    WORKSPACE_DELETE = (Permission(
        group=Group.WORKSPACE, sub_group=Group.WORKSPACE, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM, is_ee=True))

    WORKSPACE_ADD_MEMBER = (Permission(
        group=Group.WORKSPACE, sub_group=Group.WORKSPACE, operate=Operate.ADD_MEMBER, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM, is_ee=True))

    WORKSPACE_REMOVE_MEMBER = (Permission(
        group=Group.WORKSPACE, sub_group=Group.WORKSPACE, operate=Operate.REMOVE_MEMBER, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM, is_ee=True))

    WORKSPACE_WORKSPACE_READ = (Permission(
        group=Group.WORKSPACE_WORKSPACE, sub_group=Group.WORKSPACE_WORKSPACE, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM, is_ee=True))

    WORKSPACE_WORKSPACE_ADD_MEMBER = (Permission(
        group=Group.WORKSPACE_WORKSPACE, sub_group=Group.WORKSPACE_WORKSPACE, operate=Operate.ADD_MEMBER, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM, is_ee=True))

    WORKSPACE_WORKSPACE_REMOVE_MEMBER = (Permission(
        group=Group.WORKSPACE_WORKSPACE, sub_group=Group.WORKSPACE_WORKSPACE, operate=Operate.REMOVE_MEMBER, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM, is_ee=True))

    # ==================== 登录认证 ====================
    LOGIN_AUTH_READ = (Permission(
        group=Group.LOGIN_AUTH, sub_group=Group.LOGIN_AUTH, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SYSTEM_SETTING))

    LOGIN_AUTH_EDIT = (Permission(
        group=Group.LOGIN_AUTH, sub_group=Group.LOGIN_AUTH, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SYSTEM_SETTING))

    # ==================== 应用 ====================
    APPLICATION_READ = (Permission(
        group=Group.APPLICATION, sub_group=Group.APPLICATION, operate=Operate.READ, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_VIEW]))

    APPLICATION_CREATE = (Permission(
        group=Group.APPLICATION, sub_group=Group.APPLICATION, operate=Operate.CREATE, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_COPY = (Permission(
        group=Group.APPLICATION, sub_group=Group.APPLICATION, operate=Operate.COPY, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_EDIT = (Permission(
        group=Group.APPLICATION, sub_group=Group.APPLICATION, operate=Operate.EDIT, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_DELETE = (Permission(
        group=Group.APPLICATION, sub_group=Group.APPLICATION, operate=Operate.DELETE, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_IMPORT = (Permission(
        group=Group.APPLICATION, sub_group=Group.APPLICATION, operate=Operate.IMPORT, bit_index=6
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_EXPORT = (Permission(
        group=Group.APPLICATION, sub_group=Group.APPLICATION, operate=Operate.EXPORT, bit_index=7
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_PUBLISH = (Permission(
        group=Group.APPLICATION, sub_group=Group.APPLICATION, operate=Operate.PUBLISH, bit_index=8
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_BATCH_DELETE = (Permission(
        group=Group.APPLICATION, sub_group=Group.APPLICATION, operate=Operate.BATCH_DELETE, bit_index=9
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_BATCH_MOVE = (Permission(
        group=Group.APPLICATION, sub_group=Group.APPLICATION, operate=Operate.BATCH_MOVE, bit_index=10
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_RESOURCE_AUTHORIZATION = (Permission(
        group=Group.APPLICATION, sub_group=Group.APPLICATION, operate=Operate.AUTH, bit_index=11
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_RELATE_RESOURCE_VIEW = (Permission(
        group=Group.APPLICATION, sub_group=Group.APPLICATION, operate=Operate.RELATE_VIEW, bit_index=12
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    # 应用触发器
    APPLICATION_TRIGGER_READ = (Permission(
        group=Group.APPLICATION, sub_group=Group.APPLICATION, operate=Operate.TRIGGER_READ, bit_index=13
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE))

    APPLICATION_TRIGGER_CREATE = (Permission(
        group=Group.APPLICATION, sub_group=Group.APPLICATION, operate=Operate.TRIGGER_CREATE, bit_index=14
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE))

    APPLICATION_TRIGGER_EDIT = (Permission(
        group=Group.APPLICATION, sub_group=Group.APPLICATION, operate=Operate.TRIGGER_EDIT, bit_index=15
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE))

    APPLICATION_TRIGGER_DELETE = (Permission(
        group=Group.APPLICATION, sub_group=Group.APPLICATION, operate=Operate.TRIGGER_DELETE, bit_index=16
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE))

    # ==================== 应用文件夹 ====================
    APPLICATION_FOLDER_READ = (Permission(
        group=Group.APPLICATION, sub_group=Group.FOLDER, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_VIEW]))

    APPLICATION_FOLDER_CREATE = (Permission(
        group=Group.APPLICATION, sub_group=Group.FOLDER, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_FOLDER_EDIT = (Permission(
        group=Group.APPLICATION, sub_group=Group.FOLDER, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_FOLDER_DELETE = (Permission(
        group=Group.APPLICATION, sub_group=Group.FOLDER, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_FOLDER_AUTH = (Permission(
        group=Group.APPLICATION, sub_group=Group.FOLDER, operate=Operate.AUTH, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    # ==================== 应用概览 ====================
    APPLICATION_OVERVIEW_READ = (Permission(
        group=Group.APPLICATION, sub_group=Group.OVERVIEW, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_VIEW]))

    APPLICATION_OVERVIEW_EMBED = (Permission(
        group=Group.APPLICATION, sub_group=Group.OVERVIEW, operate=Operate.EMBED, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_OVERVIEW_ACCESS = (Permission(
        group=Group.APPLICATION, sub_group=Group.OVERVIEW, operate=Operate.ACCESS, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_OVERVIEW_DISPLAY = (Permission(
        group=Group.APPLICATION, sub_group=Group.OVERVIEW, operate=Operate.DISPLAY, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_OVERVIEW_API_KEY = (Permission(
        group=Group.APPLICATION, sub_group=Group.OVERVIEW, operate=Operate.API_KEY, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_OVERVIEW_PUBLIC = (Permission(
        group=Group.APPLICATION, sub_group=Group.OVERVIEW, operate=Operate.PUBLIC_ACCESS, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    # ==================== 应用接入 ====================
    APPLICATION_ACCESS_READ = (Permission(
        group=Group.APPLICATION, sub_group=Group.ACCESS, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_VIEW]))

    APPLICATION_ACCESS_EDIT = (Permission(
        group=Group.APPLICATION, sub_group=Group.ACCESS, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    # ==================== 应用对话用户 ====================
    APPLICATION_CHAT_USER_READ = (Permission(
        group=Group.APPLICATION, sub_group=Group.CHAT_USER, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_VIEW]))

    APPLICATION_CHAT_USER_EDIT = (Permission(
        group=Group.APPLICATION, sub_group=Group.CHAT_USER, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    # ==================== 应用对话日志 ====================
    APPLICATION_CHAT_LOG_READ = (Permission(
        group=Group.APPLICATION, sub_group=Group.CHAT_LOG, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_VIEW]))

    APPLICATION_CHAT_LOG_ANNOTATION = (Permission(
        group=Group.APPLICATION, sub_group=Group.CHAT_LOG, operate=Operate.ANNOTATION, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_CHAT_LOG_EXPORT = (Permission(
        group=Group.APPLICATION, sub_group=Group.CHAT_LOG, operate=Operate.EXPORT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_CHAT_LOG_CLEAR_POLICY = (Permission(
        group=Group.APPLICATION, sub_group=Group.CHAT_LOG, operate=Operate.CLEAR_POLICY, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    APPLICATION_CHAT_LOG_ADD_KNOWLEDGE = (Permission(
        group=Group.APPLICATION, sub_group=Group.CHAT_LOG, operate=Operate.ADD_KNOWLEDGE, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.RESOURCE,
                      scope=PermissionScopeConstants.WORKSPACE_RESOURCE,
                      resource_permission_group_list=[ResourcePermissionConst.APPLICATION_MANAGE]))

    # ==================== 其他 ====================
    ABOUT_READ = (Permission(
        group=Group.OTHER, sub_group=Group.OTHER, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.SYSTEM_SETTING))

    ABOUT_UPDATE = (Permission(
        group=Group.OTHER, sub_group=Group.OTHER, operate=Operate.UPDATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SYSTEM_SETTING))

    SWITCH_LANGUAGE = (Permission(
        group=Group.OTHER, sub_group=Group.OTHER, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.SYSTEM_SETTING))

    CHANGE_PASSWORD = (Permission(
        group=Group.OTHER, sub_group=Group.OTHER, operate=Operate.CREATE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.SYSTEM_SETTING))

    SYSTEM_API_KEY_EDIT = (Permission(
        group=Group.OTHER, sub_group=Group.OTHER, operate=Operate.DELETE, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN, RoleConstants.USER], category=Category.SYSTEM_SETTING))

    # ==================== 外观设置 ====================
    APPEARANCE_SETTINGS_READ = (Permission(
        group=Group.APPEARANCE_SETTINGS, sub_group=Group.APPEARANCE_SETTINGS, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SYSTEM_SETTING))

    APPEARANCE_SETTINGS_EDIT = (Permission(
        group=Group.APPEARANCE_SETTINGS, sub_group=Group.APPEARANCE_SETTINGS, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SYSTEM_SETTING))

    # ==================== 对话用户 ====================
    CHAT_USER_READ = (Permission(
        group=Group.CHAT_USER, sub_group=Group.CHAT_USER, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    CHAT_USER_CREATE = (Permission(
        group=Group.CHAT_USER, sub_group=Group.CHAT_USER, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    CHAT_USER_SYNC = (Permission(
        group=Group.CHAT_USER, sub_group=Group.CHAT_USER, operate=Operate.SYNC, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    CHAT_USER_EDIT = (Permission(
        group=Group.CHAT_USER, sub_group=Group.CHAT_USER, operate=Operate.EDIT, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    CHAT_USER_DELETE = (Permission(
        group=Group.CHAT_USER, sub_group=Group.CHAT_USER, operate=Operate.DELETE, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    CHAT_USER_GROUP = (Permission(
        group=Group.CHAT_USER, sub_group=Group.CHAT_USER, operate=Operate.USER_GROUP, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    # ==================== 对话用户组 ====================
    USER_GROUP_READ = (Permission(
        group=Group.CHAT_USER_GROUP, sub_group=Group.CHAT_USER_GROUP, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    USER_GROUP_CREATE = (Permission(
        group=Group.CHAT_USER_GROUP, sub_group=Group.CHAT_USER_GROUP, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    USER_GROUP_EDIT = (Permission(
        group=Group.CHAT_USER_GROUP, sub_group=Group.CHAT_USER_GROUP, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    USER_GROUP_DELETE = (Permission(
        group=Group.CHAT_USER_GROUP, sub_group=Group.CHAT_USER_GROUP, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    USER_GROUP_ADD_MEMBER = (Permission(
        group=Group.CHAT_USER_GROUP, sub_group=Group.CHAT_USER_GROUP, operate=Operate.ADD_MEMBER, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    USER_GROUP_REMOVE_MEMBER = (Permission(
        group=Group.CHAT_USER_GROUP, sub_group=Group.CHAT_USER_GROUP, operate=Operate.REMOVE_MEMBER, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    CHAT_USER_AUTH_READ = (Permission(
        group=Group.CHAT_USER_GROUP, sub_group=Group.CHAT_USER_GROUP, operate=Operate.READ, bit_index=6
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    # ==================== 对话用户认证 ====================
    CHAT_USER_AUTH_EDIT = (Permission(
        group=Group.CHAT_USER_AUTH, sub_group=Group.CHAT_USER_AUTH, operate=Operate.EDIT, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    # ==================== 工作空间对话用户 ====================
    WORKSPACE_CHAT_USER_READ = (Permission(
        group=Group.WORKSPACE_CHAT_USER, sub_group=Group.WORKSPACE_CHAT_USER, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    WORKSPACE_CHAT_USER_CREATE = (Permission(
        group=Group.WORKSPACE_CHAT_USER, sub_group=Group.WORKSPACE_CHAT_USER, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    WORKSPACE_CHAT_USER_EDIT = (Permission(
        group=Group.WORKSPACE_CHAT_USER, sub_group=Group.WORKSPACE_CHAT_USER, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    WORKSPACE_CHAT_USER_DELETE = (Permission(
        group=Group.WORKSPACE_CHAT_USER, sub_group=Group.WORKSPACE_CHAT_USER, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    WORKSPACE_CHAT_USER_GROUP = (Permission(
        group=Group.WORKSPACE_CHAT_USER, sub_group=Group.WORKSPACE_CHAT_USER, operate=Operate.USER_GROUP, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    # ==================== 工作空间对话用户组 ====================
    WORKSPACE_USER_GROUP_READ = (Permission(
        group=Group.CHAT_USER_GROUP, sub_group=Group.CHAT_USER_GROUP, operate=Operate.READ, bit_index=7
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    WORKSPACE_USER_GROUP_CREATE = (Permission(
        group=Group.CHAT_USER_GROUP, sub_group=Group.CHAT_USER_GROUP, operate=Operate.CREATE, bit_index=8
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    WORKSPACE_USER_GROUP_EDIT = (Permission(
        group=Group.CHAT_USER_GROUP, sub_group=Group.CHAT_USER_GROUP, operate=Operate.EDIT, bit_index=9
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    WORKSPACE_USER_GROUP_DELETE = (Permission(
        group=Group.CHAT_USER_GROUP, sub_group=Group.CHAT_USER_GROUP, operate=Operate.DELETE, bit_index=10
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    WORKSPACE_USER_GROUP_ADD_MEMBER = (Permission(
        group=Group.CHAT_USER_GROUP, sub_group=Group.CHAT_USER_GROUP, operate=Operate.ADD_MEMBER, bit_index=11
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    WORKSPACE_USER_GROUP_REMOVE_MEMBER = (Permission(
        group=Group.CHAT_USER_GROUP, sub_group=Group.CHAT_USER_GROUP, operate=Operate.REMOVE_MEMBER, bit_index=12
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.CHAT_CLIENT))

    # ==================== 工作空间用户组 ====================
    WORKSPACE_SYSTEM_USER_GROUP_READ = (Permission(
        group=Group.WORKSPACE_USER_GROUP, sub_group=Group.WORKSPACE_USER_GROUP, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    WORKSPACE_SYSTEM_USER_GROUP_CREATE = (Permission(
        group=Group.WORKSPACE_USER_GROUP, sub_group=Group.WORKSPACE_USER_GROUP, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    WORKSPACE_SYSTEM_USER_GROUP_EDIT = (Permission(
        group=Group.WORKSPACE_USER_GROUP, sub_group=Group.WORKSPACE_USER_GROUP, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    WORKSPACE_SYSTEM_USER_GROUP_DELETE = (Permission(
        group=Group.WORKSPACE_USER_GROUP, sub_group=Group.WORKSPACE_USER_GROUP, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    WORKSPACE_SYSTEM_USER_GROUP_ADD_MEMBER = (Permission(
        group=Group.WORKSPACE_USER_GROUP, sub_group=Group.WORKSPACE_USER_GROUP, operate=Operate.ADD_MEMBER, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    WORKSPACE_SYSTEM_USER_GROUP_REMOVE_MEMBER = (Permission(
        group=Group.WORKSPACE_USER_GROUP, sub_group=Group.WORKSPACE_USER_GROUP, operate=Operate.REMOVE_MEMBER,
        bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.IAM))

    # ==================== 共享工具 ====================
    SHARED_TOOL_READ = (Permission(
        group=Group.SYSTEM_TOOL, sub_group=Group.SYSTEM_TOOL, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_TOOL_CREATE = (Permission(
        group=Group.SYSTEM_TOOL, sub_group=Group.SYSTEM_TOOL, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_TOOL_EDIT = (Permission(
        group=Group.SYSTEM_TOOL, sub_group=Group.SYSTEM_TOOL, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_TOOL_DELETE = (Permission(
        group=Group.SYSTEM_TOOL, sub_group=Group.SYSTEM_TOOL, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_TOOL_IMPORT = (Permission(
        group=Group.SYSTEM_TOOL, sub_group=Group.SYSTEM_TOOL, operate=Operate.IMPORT, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_TOOL_EXPORT = (Permission(
        group=Group.SYSTEM_TOOL, sub_group=Group.SYSTEM_TOOL, operate=Operate.EXPORT, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_TOOL_PUBLISH = (Permission(
        group=Group.SYSTEM_TOOL, sub_group=Group.SYSTEM_TOOL, operate=Operate.PUBLISH, bit_index=6
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_TOOL_RELATE_RESOURCE_VIEW = (Permission(
        group=Group.SYSTEM_TOOL, sub_group=Group.SYSTEM_TOOL, operate=Operate.RELATE_VIEW, bit_index=7
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_TOOL_EXECUTE_RECORD = (Permission(
        group=Group.SYSTEM_TOOL, sub_group=Group.SYSTEM_TOOL, operate=Operate.RECORD, bit_index=8
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_TOOL_TO_WORKSPACE = (Permission(
        group=Group.SYSTEM_TOOL, sub_group=Group.SYSTEM_TOOL, operate=Operate.TO_WORKSPACE, bit_index=9
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    # ==================== 共享知识库 ====================
    SHARED_KNOWLEDGE_READ = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_KNOWLEDGE, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_CREATE = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_KNOWLEDGE, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_EDIT = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_KNOWLEDGE, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_SYNC = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_KNOWLEDGE, operate=Operate.SYNC, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_VECTOR = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_KNOWLEDGE, operate=Operate.VECTOR, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_EXPORT = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_KNOWLEDGE, operate=Operate.EXPORT, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_GENERATE = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_KNOWLEDGE, operate=Operate.GENERATE, bit_index=6
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_DELETE = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_KNOWLEDGE, operate=Operate.DELETE, bit_index=7
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_RELATE_RESOURCE_VIEW = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_KNOWLEDGE, operate=Operate.RELATE_VIEW, bit_index=8
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_TO_WORKSPACE = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_KNOWLEDGE, operate=Operate.TO_WORKSPACE, bit_index=9
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    # 共享知识库工作流
    SHARED_KNOWLEDGE_WORKFLOW_READ = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_WORKFLOW, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_WORKFLOW_EDIT = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_WORKFLOW, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_WORKFLOW_EXPORT = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_WORKFLOW, operate=Operate.EXPORT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_WORKFLOW_PUBLISH = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_WORKFLOW, operate=Operate.PUBLISH, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    # 共享知识库文档
    SHARED_KNOWLEDGE_DOCUMENT_READ = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_DOCUMENT_CREATE = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_DOCUMENT_EDIT = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_DOCUMENT_DELETE = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_DOCUMENT_SYNC = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.SYNC, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_DOCUMENT_EXPORT = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.EXPORT, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.DOWNLOAD, bit_index=6
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_DOCUMENT_GENERATE = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.GENERATE, bit_index=7
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_DOCUMENT_VECTOR = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.VECTOR, bit_index=8
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_DOCUMENT_MIGRATE = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.MIGRATE, bit_index=9
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_DOCUMENT_TAG = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.TAG, bit_index=10
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_DOCUMENT_REPLACE = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.REPLACE, bit_index=11
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_DOCUMENT_TOKEN = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.TOKEN, bit_index=12
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    # 共享知识库标签
    SHARED_KNOWLEDGE_TAG_READ = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_TAG, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_TAG_CREATE = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_TAG, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_TAG_EDIT = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_TAG, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_TAG_DELETE = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_TAG, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    # 共享知识库问题
    SHARED_KNOWLEDGE_PROBLEM_READ = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_PROBLEM, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_PROBLEM_CREATE = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_PROBLEM, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_PROBLEM_EDIT = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_PROBLEM, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_PROBLEM_DELETE = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_PROBLEM, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_PROBLEM_RELATE = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_PROBLEM, operate=Operate.RELATE, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    # 共享知识库术语库
    SHARED_KNOWLEDGE_TERMBASE_READ = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_TERMBASE, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_TERMBASE_CREATE = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_TERMBASE, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_TERMBASE_EDIT = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_TERMBASE, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_TERMBASE_DELETE = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_TERMBASE, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_TERMBASE_EXPORT = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_TERMBASE, operate=Operate.EXPORT, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    # 共享知识库命中测试
    SHARED_KNOWLEDGE_HIT_TEST = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_HIT_TEST, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    # 共享知识库对话用户
    SHARED_KNOWLEDGE_CHAT_USER_READ = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_CHAT_USER, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_KNOWLEDGE_CHAT_USER_EDIT = (Permission(
        group=Group.SYSTEM_KNOWLEDGE, sub_group=Group.SYSTEM_CHAT_USER, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    # ==================== 共享模型 ====================
    SHARED_MODEL_READ = (Permission(
        group=Group.SYSTEM_MODEL, sub_group=Group.SYSTEM_MODEL, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_MODEL_CREATE = (Permission(
        group=Group.SYSTEM_MODEL, sub_group=Group.SYSTEM_MODEL, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_MODEL_EDIT = (Permission(
        group=Group.SYSTEM_MODEL, sub_group=Group.SYSTEM_MODEL, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_MODEL_DELETE = (Permission(
        group=Group.SYSTEM_MODEL, sub_group=Group.SYSTEM_MODEL, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_MODEL_RELATE_RESOURCE_VIEW = (Permission(
        group=Group.SYSTEM_MODEL, sub_group=Group.SYSTEM_MODEL, operate=Operate.RELATE_VIEW, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    SHARED_MODEL_TO_WORKSPACE = (Permission(
        group=Group.SYSTEM_MODEL, sub_group=Group.SYSTEM_MODEL, operate=Operate.TO_WORKSPACE, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.SHARED, is_ee=True))

    # ==================== 资源管理 - 应用 ====================
    RESOURCE_APPLICATION_READ = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_RES_APPLICATION, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_EDIT = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_RES_APPLICATION, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_DELETE = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_RES_APPLICATION, operate=Operate.DELETE, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_EXPORT = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_RES_APPLICATION, operate=Operate.EXPORT, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_COPY = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_RES_APPLICATION, operate=Operate.COPY, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_AUTH = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_RES_APPLICATION, operate=Operate.AUTH, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_PUBLISH = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_RES_APPLICATION, operate=Operate.PUBLISH, bit_index=6
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_TRIGGER_READ = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_RES_APPLICATION, operate=Operate.TRIGGER_READ,
        bit_index=7
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_TRIGGER_CREATE = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_RES_APPLICATION, operate=Operate.TRIGGER_CREATE,
        bit_index=8
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_TRIGGER_EDIT = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_RES_APPLICATION, operate=Operate.TRIGGER_EDIT,
        bit_index=9
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_TRIGGER_DELETE = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_RES_APPLICATION, operate=Operate.TRIGGER_DELETE,
        bit_index=10
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_RELATE_RESOURCE_VIEW = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_RES_APPLICATION, operate=Operate.RELATE_VIEW,
        bit_index=11
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    # 资源管理 - 应用概览
    RESOURCE_APPLICATION_OVERVIEW_READ = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_OVERVIEW, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_OVERVIEW_EMBED = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_OVERVIEW, operate=Operate.EMBED, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_OVERVIEW_ACCESS = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_OVERVIEW, operate=Operate.ACCESS, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_OVERVIEW_DISPLAY = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_OVERVIEW, operate=Operate.DISPLAY, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_OVERVIEW_API_KEY = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_OVERVIEW, operate=Operate.API_KEY, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_OVERVIEW_PUBLIC = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_OVERVIEW, operate=Operate.PUBLIC_ACCESS, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    # 资源管理 - 应用接入
    RESOURCE_APPLICATION_ACCESS_READ = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_ACCESS, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_ACCESS_EDIT = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_ACCESS, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    # 资源管理 - 应用对话用户
    RESOURCE_APPLICATION_CHAT_USER_READ = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_CHAT_USER, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_CHAT_USER_EDIT = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_CHAT_USER, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    # 资源管理 - 应用对话日志
    RESOURCE_APPLICATION_CHAT_LOG_READ = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_CHAT_LOG, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_CHAT_LOG_ADD_KNOWLEDGE = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_CHAT_LOG, operate=Operate.ADD_KNOWLEDGE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_CHAT_LOG_ANNOTATION = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_CHAT_LOG, operate=Operate.ANNOTATION, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_CHAT_LOG_EXPORT = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_CHAT_LOG, operate=Operate.EXPORT, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_APPLICATION_CHAT_LOG_CLEAR_POLICY = (Permission(
        group=Group.SYSTEM_RES_APPLICATION, sub_group=Group.SYSTEM_CHAT_LOG, operate=Operate.CLEAR_POLICY, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    # ==================== 资源管理 - 知识库 ====================
    RESOURCE_KNOWLEDGE_READ = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_EDIT = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_DELETE = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.DELETE, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_SYNC = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.SYNC, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_EXPORT = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.EXPORT, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_PUBLISH = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.PUBLISH, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_VECTOR = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.VECTOR, bit_index=6
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_GENERATE = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.GENERATE, bit_index=7
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_AUTH = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.AUTH, bit_index=8
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_RELATE_RESOURCE_VIEW = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_RES_KNOWLEDGE, operate=Operate.RELATE_VIEW, bit_index=9
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    # 资源管理 - 知识库工作流
    RESOURCE_KNOWLEDGE_WORKFLOW_READ = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_WORKFLOW, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_WORKFLOW_EDIT = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_WORKFLOW, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_WORKFLOW_EXPORT = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_WORKFLOW, operate=Operate.EXPORT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_WORKFLOW_PUBLISH = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_WORKFLOW, operate=Operate.PUBLISH, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    # 资源管理 - 知识库文档
    RESOURCE_KNOWLEDGE_DOCUMENT_READ = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_DOCUMENT_CREATE = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_DOCUMENT_EDIT = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_DOCUMENT_DELETE = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_DOCUMENT_SYNC = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.SYNC, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_DOCUMENT_EXPORT = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.EXPORT, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_DOCUMENT_DOWNLOAD_SOURCE_FILE = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.DOWNLOAD, bit_index=6
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_DOCUMENT_GENERATE = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.GENERATE, bit_index=7
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_DOCUMENT_VECTOR = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.VECTOR, bit_index=8
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_DOCUMENT_MIGRATE = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.MIGRATE, bit_index=9
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_DOCUMENT_TAG = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.TAG, bit_index=10
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_DOCUMENT_REPLACE = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.REPLACE, bit_index=11
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_DOCUMENT_TOKEN = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_DOCUMENT, operate=Operate.TOKEN, bit_index=12
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    # 资源管理 - 知识库命中测试
    RESOURCE_KNOWLEDGE_HIT_TEST = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_HIT_TEST, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    # 资源管理 - 知识库问题
    RESOURCE_KNOWLEDGE_PROBLEM_READ = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_PROBLEM, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_PROBLEM_CREATE = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_PROBLEM, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_PROBLEM_EDIT = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_PROBLEM, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_PROBLEM_DELETE = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_PROBLEM, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_PROBLEM_RELATE = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_PROBLEM, operate=Operate.RELATE, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    # 资源管理 - 知识库术语库
    RESOURCE_KNOWLEDGE_TERMBASE_READ = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_TERMBASE, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_TERMBASE_CREATE = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_TERMBASE, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_TERMBASE_EDIT = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_TERMBASE, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_TERMBASE_DELETE = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_TERMBASE, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_TERMBASE_EXPORT = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_TERMBASE, operate=Operate.EXPORT, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    # 资源管理 - 知识库标签
    RESOURCE_KNOWLEDGE_TAG_READ = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_TAG, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_TAG_CREATE = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_TAG, operate=Operate.CREATE, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_TAG_EDIT = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_TAG, operate=Operate.EDIT, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_TAG_DELETE = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_TAG, operate=Operate.DELETE, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    # 资源管理 - 知识库对话用户
    RESOURCE_KNOWLEDGE_CHAT_USER_READ = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_CHAT_USER, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_KNOWLEDGE_CHAT_USER_EDIT = (Permission(
        group=Group.SYSTEM_RES_KNOWLEDGE, sub_group=Group.SYSTEM_CHAT_USER, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    # ==================== 资源管理 - 工具 ====================
    RESOURCE_TOOL_READ = (Permission(
        group=Group.SYSTEM_RES_TOOL, sub_group=Group.SYSTEM_RES_TOOL, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_TOOL_EDIT = (Permission(
        group=Group.SYSTEM_RES_TOOL, sub_group=Group.SYSTEM_RES_TOOL, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_TOOL_DELETE = (Permission(
        group=Group.SYSTEM_RES_TOOL, sub_group=Group.SYSTEM_RES_TOOL, operate=Operate.DELETE, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_TOOL_EXPORT = (Permission(
        group=Group.SYSTEM_RES_TOOL, sub_group=Group.SYSTEM_RES_TOOL, operate=Operate.EXPORT, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_TOOL_PUBLISH = (Permission(
        group=Group.SYSTEM_RES_TOOL, sub_group=Group.SYSTEM_RES_TOOL, operate=Operate.PUBLISH, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_TOOL_AUTH = (Permission(
        group=Group.SYSTEM_RES_TOOL, sub_group=Group.SYSTEM_RES_TOOL, operate=Operate.AUTH, bit_index=5
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_TOOL_RELATE_RESOURCE_VIEW = (Permission(
        group=Group.SYSTEM_RES_TOOL, sub_group=Group.SYSTEM_RES_TOOL, operate=Operate.RELATE_VIEW, bit_index=6
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_TOOL_EXECUTE_RECORD = (Permission(
        group=Group.SYSTEM_RES_TOOL, sub_group=Group.SYSTEM_RES_TOOL, operate=Operate.RECORD, bit_index=7
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_TOOL_TRIGGER_READ = (Permission(
        group=Group.SYSTEM_RES_TOOL, sub_group=Group.SYSTEM_RES_TOOL, operate=Operate.TRIGGER_READ, bit_index=8
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_TOOL_TRIGGER_CREATE = (Permission(
        group=Group.SYSTEM_RES_TOOL, sub_group=Group.SYSTEM_RES_TOOL, operate=Operate.TRIGGER_CREATE, bit_index=9
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_TOOL_TRIGGER_EDIT = (Permission(
        group=Group.SYSTEM_RES_TOOL, sub_group=Group.SYSTEM_RES_TOOL, operate=Operate.TRIGGER_EDIT, bit_index=10
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_TOOL_TRIGGER_DELETE = (Permission(
        group=Group.SYSTEM_RES_TOOL, sub_group=Group.SYSTEM_RES_TOOL, operate=Operate.TRIGGER_DELETE, bit_index=11
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    # ==================== 资源管理 - 模型 ====================
    RESOURCE_MODEL_READ = (Permission(
        group=Group.SYSTEM_RES_MODEL, sub_group=Group.SYSTEM_RES_MODEL, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_MODEL_EDIT = (Permission(
        group=Group.SYSTEM_RES_MODEL, sub_group=Group.SYSTEM_RES_MODEL, operate=Operate.EDIT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_MODEL_DELETE = (Permission(
        group=Group.SYSTEM_RES_MODEL, sub_group=Group.SYSTEM_RES_MODEL, operate=Operate.DELETE, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_MODEL_AUTH = (Permission(
        group=Group.SYSTEM_RES_MODEL, sub_group=Group.SYSTEM_RES_MODEL, operate=Operate.AUTH, bit_index=3
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    RESOURCE_MODEL_RELATE_RESOURCE_VIEW = (Permission(
        group=Group.SYSTEM_RES_MODEL, sub_group=Group.SYSTEM_RES_MODEL, operate=Operate.RELATE_VIEW, bit_index=4
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.RESOURCE, is_ee=True))

    # ==================== 操作日志 ====================
    OPERATION_LOG_READ = (Permission(
        group=Group.OPERATION_LOG, sub_group=Group.OPERATION_LOG, operate=Operate.READ, bit_index=0
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.OPERATION_LOG))

    OPERATION_LOG_EXPORT = (Permission(
        group=Group.OPERATION_LOG, sub_group=Group.OPERATION_LOG, operate=Operate.EXPORT, bit_index=1
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.OPERATION_LOG))

    OPERATION_LOG_CLEAR_POLICY = (Permission(
        group=Group.OPERATION_LOG, sub_group=Group.OPERATION_LOG, operate=Operate.CLEAR_POLICY, bit_index=2
    ), PermissionMeta(role_list=[RoleConstants.ADMIN], category=Category.OPERATION_LOG))

    def __init__(self, value, meta):
        self._value_ = value
        self.meta = meta

    def _build_workspace_permission(self, resource_id_key=None):
        def permission_factory(_, kwargs):
            return Permission(group=self.value.group,
                              sub_group=self.value.sub_group,
                              operate=self.value.operate,
                              bit_index=self.value.bit_index,
                              workspace_id=kwargs.get('workspace_id'),
                              resource_id=kwargs.get(resource_id_key) if resource_id_key else None)

        return permission_factory

    def get_workspace_application_permission(self):
        return self._build_workspace_permission(resource_id_key="application_id")

    def get_workspace_knowledge_permission(self):
        return self._build_workspace_permission(resource_id_key="knowledge_id")

    def get_workspace_model_permission(self):
        return self._build_workspace_permission(resource_id_key="model_id")

    def get_workspace_tool_permission(self):
        return self._build_workspace_permission(resource_id_key="tool_id")

    def get_workspace_permission(self):
        return self._build_workspace_permission()

    def get_workspace_permission_workspace_manage_role(self):
        """
        工作空间管理员的特权权限
        @return:  工作空间管理员特权权限
        """

        def permission_factory(_, kwargs):
            return Permission(group=self.value.group,
                              sub_group=self.value.sub_group,
                              operate=self.value.operate,
                              bit_index=self.value.bit_index,
                              workspace_id=kwargs.get('workspace_id'),
                              flag=RoleConstants.WORKSPACE_MANAGE.value)

        return permission_factory


def group_by_all_resource_permissions() -> Dict[str, List[Permission]]:
    grouped = {}

    for _permission in PermissionConstants:
        meta = _permission.meta
        if meta.resource_permission_group_list:
            for group in meta.resource_permission_group_list:
                _array = grouped.get(str(group)) or []
                _array.append(_permission)
                grouped[str(group)] = _array
    return dict(grouped)


def group_permissions_by_scope() -> Dict[str, List[Permission]]:
    grouped = {}

    for _permission in PermissionConstants:
        permission = _permission.value
        meta = _permission.meta
        if meta.scope:
            _array = grouped.get(meta.scope) or []
            _array.append(_permission)
            grouped[meta.scope] = _array
    return dict(grouped)


# 权限字符串与权限对象的Map
PERMISSION_STR_MAP = {
    _permission.value.__str__(): _permission for _permission in PermissionConstants
}

# 资源组Map
RESOURCE_PERMISSION_MAP = group_by_all_resource_permissions()

# 权限 SCOPE Map
SCOPE_PERMISSION_MAP = group_permissions_by_scope()
