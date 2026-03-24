# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： tool_workflow.py
    @date：2026/3/3 13:59
    @desc:
"""
from django.db import models

from common.mixins.app_model_mixin import AppModelMixin
import uuid_utils.compat as uuid

from tools.models import Tool


class ToolWorkflow(AppModelMixin):
    """
    知识库工作流表
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    tool = models.OneToOneField(Tool, on_delete=models.CASCADE, verbose_name="工具",
                                db_constraint=False, related_name='workflow')
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    work_flow = models.JSONField(verbose_name="工作流数据", default=dict)
    is_publish = models.BooleanField(verbose_name="是否发布", default=False, db_index=True)
    publish_time = models.DateTimeField(verbose_name="发布时间", null=True, blank=True)

    class Meta:
        db_table = "tool_workflow"


class ToolWorkflowVersion(AppModelMixin):
    """
    知识库工作流版本表 - 记录工作流历史版本
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, verbose_name="工具", db_constraint=False)
    workspace_id = models.CharField(max_length=64, verbose_name="工作空间id", default="default", db_index=True)
    name = models.CharField(verbose_name="版本名称", max_length=128, default="")
    work_flow = models.JSONField(verbose_name="工作流数据", default=dict)
    publish_user_id = models.UUIDField(verbose_name="发布者id", max_length=128, default=None, null=True)
    publish_user_name = models.CharField(verbose_name="发布者名称", max_length=128, default="")

    class Meta:
        db_table = "tool_workflow_version"
