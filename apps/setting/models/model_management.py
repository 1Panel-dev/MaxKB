# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： model_management.py
    @date：2023/10/31 15:11
    @desc:
"""
import uuid

from django.db import models

from common.mixins.app_model_mixin import AppModelMixin
from users.models import User


class Status(models.TextChoices):
    """系统设置类型"""
    SUCCESS = "SUCCESS", '成功'

    ERROR = "ERROR", "失败"

    DOWNLOAD = "DOWNLOAD", '下载中'

    PAUSE_DOWNLOAD = "PAUSE_DOWNLOAD", '暂停下载'


class PermissionType(models.TextChoices):
    PUBLIC = "PUBLIC", '公开'
    PRIVATE = "PRIVATE", "私有"


class Model(AppModelMixin):
    """
    模型数据
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")

    name = models.CharField(max_length=128, verbose_name="名称")

    status = models.CharField(max_length=20, verbose_name='设置类型', choices=Status.choices,
                              default=Status.SUCCESS)

    model_type = models.CharField(max_length=128, verbose_name="模型类型")

    model_name = models.CharField(max_length=128, verbose_name="模型名称")

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="成员用户id")

    provider = models.CharField(max_length=128, verbose_name='供应商')

    credential = models.CharField(max_length=102400, verbose_name="模型认证信息")

    meta = models.JSONField(verbose_name="模型元数据,用于存储下载,或者错误信息", default=dict)

    permission_type = models.CharField(max_length=20, verbose_name='权限类型', choices=PermissionType.choices,
                                       default=PermissionType.PRIVATE)

    def is_permission(self, user_id):
        if self.permission_type == PermissionType.PUBLIC or str(user_id) == str(self.user_id):
            return True
        return False

    class Meta:
        db_table = "model"
        unique_together = ['name', 'user_id']
