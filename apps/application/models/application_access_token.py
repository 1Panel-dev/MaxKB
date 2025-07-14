# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_access_token.py
    @date：2025/5/27 9:55
    @desc:
"""
from django.contrib.postgres.fields import ArrayField
from django.db import models

from application.models.application import Application
from common.mixins.app_model_mixin import AppModelMixin


class ApplicationAccessToken(AppModelMixin):
    """
    应用认证token
    """
    application = models.OneToOneField(Application, primary_key=True, on_delete=models.CASCADE, verbose_name="应用id")
    access_token = models.CharField(max_length=128, verbose_name="用户公开访问 认证token", unique=True)
    is_active = models.BooleanField(default=True, verbose_name="是否开启公开访问")
    access_num = models.IntegerField(default=100, verbose_name="访问次数")
    white_active = models.BooleanField(default=False, verbose_name="是否开启白名单")
    white_list = ArrayField(verbose_name="白名单列表",
                            base_field=models.CharField(max_length=128, blank=True)
                            , default=list)
    show_source = models.BooleanField(default=False, verbose_name="是否显示知识来源")
    show_exec = models.BooleanField(default=False, verbose_name="是否显示执行详情")
    authentication = models.BooleanField(default=False, verbose_name="是否需要认证")
    authentication_value = models.JSONField(verbose_name="认证的值", default=dict)

    language = models.CharField(max_length=10, verbose_name="语言", default=None, null=True)

    class Meta:
        db_table = "application_access_token"
