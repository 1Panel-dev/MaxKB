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


class Model(AppModelMixin):
    """
    模型数据
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")

    name = models.CharField(max_length=128, verbose_name="名称")

    model_type = models.CharField(max_length=128, verbose_name="模型类型")

    model_name = models.CharField(max_length=128, verbose_name="模型名称")

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="成员用户id")

    provider = models.CharField(max_length=128, verbose_name='供应商')

    credential = models.CharField(max_length=5120, verbose_name="模型认证信息")

    class Meta:
        db_table = "model"
        unique_together = ['name', 'user_id']
