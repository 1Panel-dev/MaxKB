# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： user.py
    @date：2025/4/14 10:20
    @desc:
"""
import uuid_utils.compat as uuid
from django.db import models

from common.constants.permission_constants import Group


class ChatUser(models.Model):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    email = models.EmailField(null=True, blank=True, verbose_name="邮箱", db_index=True)
    phone = models.CharField(max_length=20, verbose_name="电话", default="")
    nick_name = models.CharField(max_length=150, verbose_name="昵称", unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, verbose_name="用户名", db_index=True)
    password = models.CharField(max_length=150, verbose_name="密码")
    source = models.CharField(max_length=10, verbose_name="来源", default="LOCAL", db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True, db_index=True)
    update_time = models.DateTimeField(verbose_name="修改时间", auto_now=True, null=True, db_index=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "chat_user"


class UserGroup(models.Model):
    id = models.CharField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=150, verbose_name="名称", unique=True, db_index=True)

    class Meta:
        db_table = "user_group"


class UserGroupRelation(models.Model):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    user = models.ForeignKey(ChatUser, on_delete=models.CASCADE, verbose_name="用户")
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, verbose_name="用户组")

    class Meta:
        db_table = "user_group_relation"


class ResourceType(models.TextChoices):
    """资源类型"""
    KNOWLEDGE = Group.KNOWLEDGE.value, '知识库'
    APPLICATION = Group.APPLICATION.value, '应用'


class ResourceChatUserAuthorize(models.Model):
    """
    资源对话用户授权表
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True,
                                    null=True)
    user_group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, verbose_name="用户组")
    user = models.ForeignKey(ChatUser, on_delete=models.CASCADE, verbose_name="用户")
    resource_id = models.UUIDField(max_length=128, verbose_name="资源id", db_index=True)
    resource_type = models.CharField(verbose_name="资源类型", choices=ResourceType.choices, db_index=True)
    is_auth = models.BooleanField(verbose_name="是否授权")

    class Meta:
        db_table = "resource_chat_user_authorize"
        unique_together = ('user_group_id', 'resource_type', 'resource_id', 'user_id')


class ResourceChatUserGroupAuthorize(models.Model):
    """
    资源对话用户组授权表
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True,
                                    null=True)
    user_group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, verbose_name="用户组")
    resource_id = models.UUIDField(max_length=128, verbose_name="资源id", db_index=True)
    resource_type = models.CharField(verbose_name="资源类型", choices=ResourceType.choices, db_index=True)
    is_auth = models.BooleanField(verbose_name="是否授权")

    class Meta:
        db_table = "resource_chat_user_group_authorize"
        unique_together = ('user_group_id', 'resource_type', 'resource_id')
