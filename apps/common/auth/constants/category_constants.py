# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： category_constants.py
    @date：2026/8/3 17:31
    @desc: 一级目录分类常量（最顶层分类）
"""
from enum import Enum
from django.utils.translation import gettext_lazy as _


class Category(Enum):
    """
    一级目录（最顶层分类），用于在 parent_group 之上再加一层分类
    """
    # 身份与权限
    IAM = ("IAM", _("IAM"))
    # 资源管理
    RESOURCE = ("RESOURCE", _("Resource"))
    # 共享资源
    SHARED = ("SHARED", _("Shared"))
    # 对话客户端
    CHAT_CLIENT = ("CHAT_CLIENT", _("Chat Client"))
    # 操作日志
    OPERATION_LOG = ("OPERATION_LOG", _("Operation Log"))
    # 系统设置
    SYSTEM_SETTING = ("SYSTEM_SETTING", _("System Setting"))
    # 工作空间
    WORKSPACE = ("WORKSPACE", _("Workspace"))
    # 其他
    OTHER = ("OTHER", _("Other"))

    def __init__(self, value, label):
        self._value_ = value
        self.label = label
