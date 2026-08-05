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

from common.constants.resource_permission_constants import ResourceAuthType, ResourcePermissionConstants, \
    AuthTargetType

from users.models.user_group import SystemUserGroup


class WorkspaceUserGroupResourcePermission(models.Model):
    """
    工作空间用户组资源权限表
    用于管理当前工作空间下用户组对某一个应用或者知识库的操作权限
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")

    workspace_id = models.CharField(max_length=128, verbose_name="工作空间id", default="default", db_index=True)

    user_group = models.ForeignKey(SystemUserGroup, on_delete=models.CASCADE, verbose_name="用户组id", db_index=True)

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
                                                             choices=ResourcePermissionConstants.choices,
                                                             default=ResourcePermissionConstants.VIEW))

    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, db_index=True)

    update_time = models.DateTimeField(verbose_name="修改时间", auto_now=True, db_index=True)

    class Meta:
        db_table = "workspace_user_group_resource_permission"
        unique_together = ('workspace_id', 'user_group', 'auth_target_type', 'target')
