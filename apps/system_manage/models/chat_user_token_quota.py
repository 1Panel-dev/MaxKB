# coding=utf-8
"""
@project: MaxKB
@file： chat_user_token_quota.py
@desc: 对话用户Token配额模型
"""

import uuid_utils.compat as uuid
from django.db import models

from common.exception.app_exception import AppApiException
from common.mixins.app_model_mixin import AppModelMixin
from dateutil.relativedelta import relativedelta
from django.utils import timezone


class QuotaType(models.TextChoices):
    UNLIMITED = "UNLIMITED", "不限额"
    PERIODIC = "PERIODIC", "按周期限制"


class PeriodType(models.TextChoices):
    DAY = "DAY", "天"
    WEEK = "WEEK", "周"
    MONTH = "MONTH", "月"


class ChatUserTokenQuota(AppModelMixin):
    """
    对话用户Token配额
    """

    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")

    user_id = models.CharField(max_length=128, unique=True, verbose_name="用户id", db_index=True)

    quota_type = models.CharField(
        max_length=20, choices=QuotaType.choices, default=QuotaType.UNLIMITED, verbose_name="配额模式"
    )

    period_type = models.CharField(
        max_length=10, choices=PeriodType.choices, null=True, blank=True, verbose_name="周期单位"
    )

    period_value = models.PositiveIntegerField(null=True, blank=True, verbose_name="周期数量")

    token_limit = models.BigIntegerField(null=True, blank=True, verbose_name="Tokens上限")

    # 统计字段
    used_tokens = models.BigIntegerField(default=0, verbose_name="当前周期已使用Tokens")
    total_tokens = models.BigIntegerField(default=0, verbose_name="累计Tokens")

    period_end = models.DateTimeField(null=True, blank=True, verbose_name="当前周期结束时间")

    class Meta:
        db_table = "chat_user_token_quota"

    def check_and_reset(self):
        if self.quota_type != QuotaType.PERIODIC or self.period_end is None:
            return
        now = timezone.now()
        if now < self.period_end:
            return
        while self.period_end <= now:
            self.period_end += relativedelta(**{f"{self.period_type.lower()}s": self.period_value})
        self.used_tokens = 0
        self.save(update_fields=["used_tokens", "period_end"])

    @classmethod
    def consume(cls, user_id, amount):
        if amount <= 0:
            return
        quota = cls.objects.filter(user_id=user_id).first()
        if quota is None:
            # 所有消费用户都创建统计行，匿名用户也累计使用量
            quota, _ = cls.objects.get_or_create(
                user_id=user_id,
                defaults={"quota_type": QuotaType.UNLIMITED},
            )
        if quota.quota_type == QuotaType.UNLIMITED:
            # 不限额：只累计使用量，不校验上限
            quota.used_tokens += amount
            quota.total_tokens += amount
            quota.save(update_fields=["used_tokens", "total_tokens"])
            return
        quota.check_and_reset()
        if quota.used_tokens + amount > quota.token_limit:
            raise AppApiException(
                500, _("The token quota for the current period has been exhausted. Please contact the administrator.")
            )
        quota.used_tokens += amount
        quota.total_tokens += amount
        quota.save(update_fields=["used_tokens", "total_tokens"])
