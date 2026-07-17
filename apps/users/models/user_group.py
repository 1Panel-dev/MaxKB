# coding=utf-8
import uuid_utils.compat as uuid

from django.db import models

from users.models import User


class SystemUserGroup(models.Model):
    id = models.CharField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=150, verbose_name="名称", unique=True, db_index=True)
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True, db_index=True)
    update_time = models.DateTimeField(verbose_name="修改时间", auto_now=True, null=True, db_index=True)

    class Meta:
        db_table = "system_user_group"
        unique_together = ("workspace_id", "name")


class SystemUserGroupRelation(models.Model):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    group = models.ForeignKey(SystemUserGroup, on_delete=models.CASCADE, verbose_name="用户组")

    class Meta:
        db_table = "system_user_group_relation"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "group"],
                name="uniq_user_group_relation"
            )
        ]

