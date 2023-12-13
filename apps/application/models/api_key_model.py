# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： api_key_model.py
    @date：2023/11/14 17:15
    @desc:
"""
import uuid

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
    class Meta:
        db_table = "application_api_key"


class ApplicationAccessToken(AppModelMixin):
    """
    应用认证token
    """
    application = models.OneToOneField(Application, primary_key=True, on_delete=models.CASCADE, verbose_name="应用id")
    access_token = models.CharField(max_length=128, verbose_name="用户公开访问 认证token", unique=True)
    is_active = models.BooleanField(default=True, verbose_name="是否开启公开访问")

    class Meta:
        db_table = "application_access_token"
