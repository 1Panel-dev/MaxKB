# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： trigger.py.py
    @date：2026/1/9 15:33
    @desc:
"""
import uuid_utils.compat as uuid

from django.db import models

from common.encoder.encoder import SystemEncoder
from common.mixins.app_model_mixin import AppModelMixin
from knowledge.models.knowledge_action import State
from users.models import User


class TriggerTypeChoices(models.TextChoices):
    SCHEDULED = 'SCHEDULED'
    EVENT = 'EVENT'


class TriggerTaskTypeChoices(models.TextChoices):
    APPLICATION = 'APPLICATION'
    TOOL = 'TOOL'


class Trigger(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    name = models.CharField(max_length=128, verbose_name="触发器名称", db_index=True)
    desc = models.CharField(max_length=512, verbose_name="引用描述", default="")
    trigger_type = models.CharField(verbose_name="触发器类型", choices=TriggerTypeChoices.choices,
                                    default=TriggerTypeChoices.SCHEDULED, max_length=256)
    trigger_setting = models.JSONField(default=dict)
    meta = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, db_constraint=False, blank=True, null=True)

    class Meta:
        db_table = "event_trigger"


class TriggerTask(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    trigger = models.ForeignKey(Trigger, on_delete=models.CASCADE)
    source_type = models.CharField(verbose_name="触发器任务类型", choices=TriggerTaskTypeChoices.choices,
                                   default=TriggerTaskTypeChoices.APPLICATION, max_length=256
                                   )
    source_id = models.UUIDField(verbose_name="资源id")
    is_active = models.BooleanField(default=True, db_index=True)
    parameter = models.JSONField(default=list)
    meta = models.JSONField(default=dict)

    class Meta:
        unique_together = [('trigger', 'source_id', 'source_type')]
        db_table = "event_trigger_task"


class TaskRecord(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")

    trigger = models.ForeignKey(Trigger, on_delete=models.CASCADE)

    trigger_task_id = models.UUIDField(max_length=128, default=uuid.uuid7, editable=False, verbose_name="触发器任务id")

    source_type = models.CharField(verbose_name="触发器任务类型", choices=TriggerTaskTypeChoices.choices,
                                   default=TriggerTaskTypeChoices.APPLICATION, max_length=256)
    source_id = models.UUIDField(verbose_name="资源id")
    task_record_id = models.UUIDField(verbose_name="任务记录id")
    meta = models.JSONField(default=dict, encoder=SystemEncoder)
    state = models.CharField(verbose_name='状态', max_length=20,
                             choices=State.choices,
                             default=State.STARTED)
    run_time = models.FloatField(verbose_name="运行时长", default=0)

    class Meta:
        db_table = "event_trigger_task_record"
