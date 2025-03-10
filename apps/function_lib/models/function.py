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
from users.models import User


class PermissionType(models.TextChoices):
    PUBLIC = "PUBLIC", '公开'
    PRIVATE = "PRIVATE", "私有"

class FunctionType(models.TextChoices):
    INTERNAL = "INTERNAL", '内置'
    PUBLIC = "PUBLIC", "公开"


class FunctionLib(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户id")
    name = models.CharField(max_length=64, verbose_name="函数名称")
    desc = models.CharField(max_length=128, verbose_name="描述")
    code = models.CharField(max_length=102400, verbose_name="python代码")
    input_field_list = ArrayField(verbose_name="输入字段列表",
                                  base_field=models.JSONField(verbose_name="输入字段", default=dict)
                                  , default=list)
    init_field_list = models.JSONField(verbose_name="启动字段列表", default=list)
    icon = models.CharField(max_length=256, verbose_name="函数库icon", default="/ui/favicon.ico")
    is_active = models.BooleanField(default=True)
    permission_type = models.CharField(max_length=20, verbose_name='权限类型', choices=PermissionType.choices,
                                       default=PermissionType.PRIVATE)
    function_type = models.CharField(max_length=20, verbose_name='函数类型', choices=FunctionType.choices,
                                       default=FunctionType.PUBLIC)
    template_id =  models.UUIDField(max_length=128, verbose_name="模版id", null=True, default=None)
    init_params = models.CharField(max_length=102400, verbose_name="初始化参数", null=True)

    class Meta:
        db_table = "function_lib"
