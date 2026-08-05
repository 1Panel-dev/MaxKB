# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： resource_auth_type_constants.py
    @date：2026/8/4 15:31
    @desc:
"""

from django.db import models


class ResourceAuthType(models.TextChoices):
    """
    资源授权类型
    """
    "当授权类型是Role时候"
    ROLE = "ROLE"

    """资源权限组"""
    RESOURCE_PERMISSION_GROUP = "RESOURCE_PERMISSION_GROUP"
