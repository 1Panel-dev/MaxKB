# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： resource_mapping.py
    @date：2025/12/19 15:41
    @desc:
"""
from django.db import models
import uuid_utils.compat as uuid

from common.constants.permission_constants import Group
from common.mixins.app_model_mixin import AppModelMixin


class ResourceType(models.TextChoices):
    KNOWLEDGE = Group.KNOWLEDGE.value, '知识库'
    APPLICATION = Group.APPLICATION.value, '应用'
    TOOL = Group.TOOL.value, '工具'
    MODEL = Group.MODEL.value, '模型'


class ResourceMapping(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    source_type = models.CharField(verbose_name="关联资源类型", choices=ResourceType.choices, db_index=True)
    target_type = models.CharField(verbose_name="被关联资源类型", choices=ResourceType.choices, db_index=True)
    source_id = models.CharField(max_length=128, verbose_name="关联资源id", db_index=True)
    target_id = models.CharField(max_length=128, verbose_name="被关联资源id", db_index=True)

    class Meta:
        db_table = "resource_mapping"
