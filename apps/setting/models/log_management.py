# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： log_management.py
    @date：2025/3/17 9:54
    @desc:
"""
import uuid

from django.db import models

from common.encoder.encoder import SystemEncoder
from common.mixins.app_model_mixin import AppModelMixin


class Log(AppModelMixin):
    """
    审计日志
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")

    menu = models.CharField(max_length=128, verbose_name="操作菜单")

    operate = models.CharField(max_length=128, verbose_name="操作")

    operation_object = models.JSONField(verbose_name="操作对象", default=dict, encoder=SystemEncoder)

    user = models.JSONField(verbose_name="用户信息", default=dict)

    status = models.IntegerField(verbose_name="状态")

    ip_address = models.CharField(max_length=128, verbose_name="ip地址")

    details = models.JSONField(verbose_name="详情", default=dict, encoder=SystemEncoder)

    class Meta:
        db_table = "log"
