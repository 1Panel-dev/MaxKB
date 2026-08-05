# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： resource_permission_constants.py
    @date：2026/8/4 15:38
    @desc:
"""
from django.db import models


class ResourcePermissionConstants(models.TextChoices):
    """
    资源权限组
    """
    # 查看
    VIEW = "VIEW"
    # 管理
    MANAGE = "MANAGE"
    # 角色
    ROLE = "ROLE"

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


class AuthTargetType(models.TextChoices):
    """授权目标"""
    KNOWLEDGE = 'KNOWLEDGE', '知识库'
    APPLICATION = 'APPLICATION', '应用'
    TOOL = 'TOOL', '工具'
    MODEL = 'MODEL', '模型'
