# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： workspace_permission.py
    @date：2025/4/16 18:25
    @desc:
"""

import uuid_utils.compat as uuid
from django.contrib.postgres.fields import ArrayField
from django.db import models

from common.constants.permission_constants import Group, ResourcePermissionGroup, ResourceAuthType, \
    ResourcePermissionRole, ResourcePermission
from users.models import User


class AuthTargetType(models.TextChoices):
    """授权目标"""
    KNOWLEDGE = Group.KNOWLEDGE.value, '知识库'
    APPLICATION = Group.APPLICATION.value, '应用'
    TOOL = Group.TOOL.value, '工具'
    MODEL = Group.MODEL.value, '模型'


class WorkspaceUserResourcePermission(models.Model):
    """
    工作空间用户资源权限表
    用于管理当前工作空间是否有权限操作 某一个应用或者知识库
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")

    workspace_id = models.CharField(max_length=128, verbose_name="工作空间id", default="default", db_index=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="工作空间下的用户")

    auth_target_type = models.CharField(verbose_name='授权目标', max_length=128, choices=AuthTargetType.choices,
                                        default=AuthTargetType.KNOWLEDGE, db_index=True)
    # 授权的知识库或者应用的id
    target = models.CharField(max_length=128, verbose_name="知识库/应用id", db_index=True)

    # 授权类型 如果是Role那么就是角色的权限  如果是PERMISSION
    auth_type = models.CharField(default=False, verbose_name="授权类型", choices=ResourceAuthType.choices,
                                 db_default=ResourceAuthType.ROLE, db_index=True)
    # 资源权限列表
    permission_list = ArrayField(verbose_name="权限列表",
                                 default=list,
                                 base_field=models.CharField(max_length=256,
                                                             blank=True,
                                                             choices=ResourcePermission.choices + ResourcePermissionRole.choices,
                                                             default=ResourcePermission.VIEW))

    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, db_index=True)

    update_time = models.DateTimeField(verbose_name="修改时间", auto_now=True, db_index=True)

    class Meta:
        db_table = "workspace_user_resource_permission"
        unique_together = ('workspace_id', 'user', 'auth_target_type', 'target')
