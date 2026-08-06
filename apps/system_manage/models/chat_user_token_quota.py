# coding=utf-8
"""
    @project: MaxKB
    @file： chat_user_token_quota.py
    @desc: 对话用户Token配额模型
"""
import uuid_utils.compat as uuid
from django.db import models

from common.mixins.app_model_mixin import AppModelMixin


class QuotaType(models.TextChoices):
    UNLIMITED = 'UNLIMITED', '不限额'
    PERIODIC = 'PERIODIC', '按周期限制'


class PeriodType(models.TextChoices):
    DAY = 'DAY', '天'
    WEEK = 'WEEK', '周'
    MONTH = 'MONTH', '月'


class ChatUserTokenQuota(AppModelMixin):
    """
    对话用户Token配额
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")

    user_id = models.UUIDField(max_length=128, unique=True, verbose_name="用户id")

    quota_type = models.CharField(max_length=20, choices=QuotaType.choices,
                                  default=QuotaType.UNLIMITED, verbose_name="配额模式")

    period_type = models.CharField(max_length=10, choices=PeriodType.choices,
                                   null=True, blank=True, verbose_name="周期单位")

    period_value = models.PositiveIntegerField(null=True, blank=True, verbose_name="周期数量")

    token_limit = models.BigIntegerField(null=True, blank=True, verbose_name="Tokens上限")

    # 统计字段
    used_tokens = models.BigIntegerField(default=0, verbose_name="当前周期已使用Tokens")
    total_tokens = models.BigIntegerField(default=0, verbose_name="累计Tokens")

    period_end = models.DateTimeField(null=True, blank=True, verbose_name="当前周期结束时间")

    class Meta:
        db_table = "chat_user_token_quota"
