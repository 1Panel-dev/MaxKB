# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： workflow.py
    @date：2025/5/7 15:44
    @desc:
"""
from django.db import models
import uuid_utils.compat as uuid


class WorkflowType(models.TextChoices):
    # 应用
    APPLICATION = "APPLICATION"
    # 知识库
    KNOWLEDGE = "KNOWLEDGE"
    # ....


class Workflow(models.Model):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    workflow = models.JSONField(verbose_name="工作流数据", default=dict)
    type = models.CharField(verbose_name="工作流类型", choices=WorkflowType.choices, default=WorkflowType.APPLICATION)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="修改时间", auto_now=True)

    class Meta:
        db_table = "workflow"
        ordering = ['update_time']
