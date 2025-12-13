# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： knowledge_action.py
    @date：2025/11/18 17:59
    @desc:
"""
import uuid_utils.compat as uuid

from django.db import models

from common.encoder.encoder import SystemEncoder
from common.mixins.app_model_mixin import AppModelMixin
from knowledge.models import Knowledge


class State(models.TextChoices):
    # 等待
    PENDING = 'PENDING'
    # 执行中
    STARTED = 'STARTED'
    # 成功
    SUCCESS = 'SUCCESS'
    # 失败
    FAILURE = 'FAILURE'
    # 取消任务
    REVOKE = 'REVOKE'
    # 取消成功
    REVOKED = 'REVOKED'


class KnowledgeAction(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")

    knowledge = models.ForeignKey(Knowledge, on_delete=models.DO_NOTHING, verbose_name="知识库", db_constraint=False)

    state = models.CharField(verbose_name='状态', max_length=20,
                             choices=State.choices,
                             default=State.STARTED)

    details = models.JSONField(verbose_name="执行详情", default=dict, encoder=SystemEncoder)

    run_time = models.FloatField(verbose_name="运行时长", default=0)

    meta = models.JSONField(verbose_name="元数据", default=dict)

    class Meta:
        db_table = "knowledge_action"
