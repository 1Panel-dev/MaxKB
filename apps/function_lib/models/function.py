# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： function_lib.py
    @date：2024/8/2 14:59
    @desc:
"""
import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models

from common.mixins.app_model_mixin import AppModelMixin


class FunctionLib(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=64, verbose_name="函数名称")
    desc = models.CharField(max_length=128, verbose_name="描述")
    code = models.CharField(max_length=102400, verbose_name="python代码")
    input_field_list = ArrayField(verbose_name="输入字段列表",
                                  base_field=models.JSONField(verbose_name="输入字段", default=dict)
                                  , default=list)

    class Meta:
        db_table = "function_lib"
