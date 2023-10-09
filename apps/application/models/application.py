# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： application.py
    @date：2023/9/25 14:24
    @desc:
"""
import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models

from common.mixins.app_model_mixin import AppModelMixin
from dataset.models.data_set import DataSet
from users.models import User


class Application(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=128, verbose_name="应用名称")
    desc = models.CharField(max_length=128, verbose_name="引用描述")
    prologue = models.CharField(max_length=1024, verbose_name="开场白")
    example = ArrayField(verbose_name="示例列表", base_field=models.CharField(max_length=256, blank=True))
    status = models.BooleanField(default=True, verbose_name="是否发布")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = "application"


class ApplicationDatasetMapping(AppModelMixin):
    application = models.ForeignKey(Application, on_delete=models.DO_NOTHING)
    dataset = models.ForeignKey(DataSet, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = "application_dataset_mapping"
