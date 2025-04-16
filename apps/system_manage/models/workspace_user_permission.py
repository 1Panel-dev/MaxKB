# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： workspace_permission.py
    @date：2025/4/16 18:25
    @desc:
"""

import uuid_utils.compat as uuid
from django.db import models

from common.constants.permission_constants import Group
from users.models import User


class AuthTargetType(models.TextChoices):
    """授权目标"""
    KNOWLEDGE = Group.KNOWLEDGE.value, '知识库'
    APPLICATION = Group.APPLICATION.value, '应用'


class WorkspaceUserPermission(models.Model):
    """
    工作空间用户资源权限表
    用于管理当前工作空间是否有权限操作 某一个应用或者知识库
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")

    workspace_id = models.CharField(max_length=128, verbose_name="工作空间id", default="default")

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="工作空间下的用户")

    auth_target_type = models.CharField(verbose_name='授权目标', max_length=128, choices=AuthTargetType.choices,
                                        default=AuthTargetType.KNOWLEDGE)
    # 授权的知识库或者应用的id
    target = models.UUIDField(max_length=128, verbose_name="知识库/应用id")

    # 是否授权
    is_auth = models.BooleanField(default=False, verbose_name="是否授权")

    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    update_time = models.DateTimeField(verbose_name="修改时间", auto_now=True)

    class Meta:
        db_table = "workspace_user_permission"
