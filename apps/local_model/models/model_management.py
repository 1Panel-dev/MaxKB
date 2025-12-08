# coding=utf-8
import uuid_utils.compat as uuid

from django.db import models

from common.mixins.app_model_mixin import AppModelMixin
from local_model.models.user import User


class Status(models.TextChoices):
    """系统设置类型"""
    SUCCESS = "SUCCESS", '成功'

    ERROR = "ERROR", "失败"

    DOWNLOAD = "DOWNLOAD", '下载中'

    PAUSE_DOWNLOAD = "PAUSE_DOWNLOAD", '暂停下载'


class Model(AppModelMixin):
    """
    模型数据
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")

    name = models.CharField(max_length=128, verbose_name="名称", db_index=True)

    status = models.CharField(max_length=20, verbose_name='设置类型', choices=Status.choices,
                              default=Status.SUCCESS, db_index=True)

    model_type = models.CharField(max_length=128, verbose_name="模型类型", db_index=True)

    model_name = models.CharField(max_length=128, verbose_name="模型名称", db_index=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, db_constraint=False, blank=True, null=True)

    provider = models.CharField(max_length=128, verbose_name='供应商', db_index=True)

    credential = models.CharField(max_length=102400, verbose_name="模型认证信息")

    meta = models.JSONField(verbose_name="模型元数据,用于存储下载,或者错误信息", default=dict)

    model_params_form = models.JSONField(verbose_name="模型参数配置", default=list)
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)

    class Meta:
        db_table = "model"
        unique_together = ['name', 'workspace_id']
