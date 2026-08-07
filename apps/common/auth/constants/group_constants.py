# coding=utf-8
"""
@project: MaxKB
@Author：虎虎虎
@file： group_constants.py
@date：2026/8/3 17:31
@desc: 权限分组常量，用于菜单和权限分类
"""

from enum import Enum

from django.utils.translation import gettext_lazy as _


class Group(Enum):
    """
    权限组 一个组一般对应前端一个菜单
    使用方式：
    - 无子分组: group=Group.TOOL, sub_group=Group.TOOL
    - 有子分组: group=Group.TOOL, sub_group=Group.FOLDER
    """

    # 用户管理
    USER = ("USER_MANAGEMENT", _("User Management"))

    # 资源主分组
    APPLICATION = ("APPLICATION", _("Application"))
    KNOWLEDGE = ("KNOWLEDGE", _("Knowledge"))
    MODEL = ("MODEL", _("Model"))
    TOOL = ("TOOL", _("Tool"))
    TRIGGER = ("TRIGGER", _("Trigger"))

    # 子分组 - 文件夹
    FOLDER = ("FOLDER", _("Folder"))

    # 子分组 - 知识库
    DOCUMENT = ("DOCUMENT", _("Document"))
    WORKFLOW = ("WORKFLOW", _("Workflow"))
    TAG = ("TAG", _("Tag"))
    PROBLEM = ("PROBLEM", _("Problem"))
    TERMBASE = ("TERMBASE", _("Termbase"))
    HIT_TEST = ("HIT_TEST", _("Hit-Test"))

    # 子分组 - 应用
    OVERVIEW = ("OVERVIEW", _("Overview"))
    ACCESS = ("ACCESS", _("Application Access"))
    CHAT_LOG = ("CHAT_LOG", _("Conversation log"))
    CHAT_USER = ("CHAT_USER", _("Dialogue users"))

    # 子分组 - 对话用户（知识库）
    KNOWLEDGE_CHAT_USER = ("KNOWLEDGE_CHAT_USER", _("Dialogue users"))

    # 系统功能分组
    ROLE = ("ROLE", _("Role Management"))
    WORKSPACE = ("WORKSPACE", _("Workspace"))
    USER_GROUP = ("USER_GROUP", _("User Group"))
    EMAIL_SETTING = ("EMAIL_SETTING", _("Email Setting"))
    LOGIN_AUTH = ("LOGIN_AUTH", _("Login Auth"))
    APPEARANCE_SETTINGS = ("APPEARANCE_SETTINGS", _("Appearance Settings"))
    DISPLAY_SETTINGS = ("DISPLAY_SETTINGS", _("Display Settings"))

    # 对话相关
    CHAT_USER_GROUP = ("CHAT_USER_GROUP", _("Chat User Group"))
    CHAT_USER_AUTH = ("CHAT_USER_AUTH", _("Chat User Auth"))
    PORTAL = ("PORTAL", _("portal"))
    # 其他
    OTHER = ("OTHER", _("Other"))
    HOMEPAGE = ("HOMEPAGE", _("Home page"))
    OPERATION_LOG = ("OPERATION_LOG", _("Operation Log"))

    # 资源授权分组
    RESOURCE_PERMISSION = ("RESOURCE_PERMISSION", _("Resource Permission"))
    APPLICATION_RESOURCE_PERMISSION = (
        "APPLICATION_RESOURCE_PERMISSION",
        _("Application"),
    )
    KNOWLEDGE_RESOURCE_PERMISSION = ("KNOWLEDGE_RESOURCE_PERMISSION", _("Knowledge"))
    TOOL_RESOURCE_PERMISSION = ("TOOL_RESOURCE_PERMISSION", _("Tool"))
    MODEL_RESOURCE_PERMISSION = ("MODEL_RESOURCE_PERMISSION", _("Model"))

    # 工作空间分组
    WORKSPACE_ROLE = ("WORKSPACE_ROLE", _("Role Management"))
    WORKSPACE_WORKSPACE = ("WORKSPACE_WORKSPACE", _("Workspace"))
    WORKSPACE_USER_GROUP = ("WORKSPACE_USER_GROUP", _("User Group"))
    WORKSPACE_RESOURCE_PERMISSION = ("WORKSPACE_RESOURCE_PERMISSION", _("Resource Permission"))
    WORKSPACE_CHAT_USER = ("WORKSPACE_CHAT_USER", _("Chat User"))
    WORKSPACE_CHAT_USER_GROUP = ("WORKSPACE_CHAT_USER_GROUP", _("Chat User Group"))

    # 用户级分组
    USER_HOMEPAGE = ("USER_HOMEPAGE", _("Home page"))
    USER_APPLICATION = ("USER_APPLICATION", _("Application"))
    USER_KNOWLEDGE = ("USER_KNOWLEDGE", _("Knowledge"))
    USER_MODEL = ("USER_MODEL", _("Model"))
    USER_TOOL = ("USER_TOOL", _("Tool"))
    USER_OTHER = ("USER_OTHER", _("Other"))

    # 共享资源分组
    SYSTEM_KNOWLEDGE = ("SYSTEM_KNOWLEDGE", _("Knowledge"))
    SYSTEM_MODEL = ("SYSTEM_MODEL", _("Model"))
    SYSTEM_TOOL = ("SYSTEM_TOOL", _("Tool"))

    # 资源管理分组
    SYSTEM_RES_APPLICATION = ("SYSTEM_RESOURCE_APPLICATION", _("Application"))
    SYSTEM_RES_KNOWLEDGE = ("SYSTEM_RESOURCE_KNOWLEDGE", _("Knowledge"))
    SYSTEM_RES_TOOL = ("SYSTEM_RESOURCE_TOOL", _("Tool"))
    SYSTEM_RES_MODEL = ("SYSTEM_RESOURCE_MODEL", _("Model"))

    # 系统资源子分组
    SYSTEM_DOCUMENT = ("SYSTEM_DOCUMENT", _("Document"))
    SYSTEM_WORKFLOW = ("SYSTEM_WORKFLOW", _("Workflow"))
    SYSTEM_TAG = ("SYSTEM_TAG", _("Tag"))
    SYSTEM_PROBLEM = ("SYSTEM_PROBLEM", _("Problem"))
    SYSTEM_TERMBASE = ("SYSTEM_TERMBASE", _("Termbase"))
    SYSTEM_HIT_TEST = ("SYSTEM_HIT_TEST", _("Hit-Test"))
    SYSTEM_CHAT_USER = ("SYSTEM_CHAT_USER", _("Dialogue users"))
    SYSTEM_OVERVIEW = ("SYSTEM_OVERVIEW", _("Overview"))
    SYSTEM_ACCESS = ("SYSTEM_ACCESS", _("Application Access"))
    SYSTEM_CHAT_LOG = ("SYSTEM_CHAT_LOG", _("Conversation log"))

    def __init__(self, value, label):
        self._value_ = value
        self.label = label

    def __str__(self):
        return self.value
