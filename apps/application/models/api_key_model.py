# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： api_key_model.py
    @date：2023/11/14 17:15
    @desc:
"""
import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models

from application.models import Application
from common.mixins.app_model_mixin import AppModelMixin
from users.models import User


class ApplicationApiKey(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    secret_key = models.CharField(max_length=1024, verbose_name="秘钥", unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户id")
    application = models.ForeignKey(Application, on_delete=models.CASCADE, verbose_name="应用id")
    is_active = models.BooleanField(default=True, verbose_name="是否开启")
    allow_cross_domain = models.BooleanField(default=False, verbose_name="是否允许跨域")
    cross_domain_list = ArrayField(verbose_name="跨域列表",
                                   base_field=models.CharField(max_length=128, blank=True)
                                   , default=list)

    class Meta:
        db_table = "application_api_key"


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

    class Meta:
        db_table = "application_access_token"


class ApplicationPublicAccessClient(AppModelMixin):
    id = models.UUIDField(max_length=128, primary_key=True, verbose_name="公共访问链接客户端id")
    application = models.ForeignKey(Application, on_delete=models.CASCADE, verbose_name="应用id")
    access_num = models.IntegerField(default=0, verbose_name="访问总次数次数")
    intraday_access_num = models.IntegerField(default=0, verbose_name="当日访问次数")

    class Meta:
        db_table = "application_public_access_client"
