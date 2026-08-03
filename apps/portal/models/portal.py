# coding=utf-8

import uuid_utils.compat as uuid
from common.encoder.encoder import SystemEncoder
from common.mixins.app_model_mixin import AppModelMixin
from django.db import models


class Portal(AppModelMixin):
    """
    门户配置
    """
    # 基础信息
    name = models.CharField(
        max_length=64,
        verbose_name="门户名称",
        default="智能体门户"
    )

    description = models.TextField(
        null=True,
        blank=True,
        max_length=256,
        verbose_name="门户描述"
    )

    logo = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        verbose_name="门户Logo地址"
    )

    tab_logo = models.CharField(
        max_length=512,
        null=True,
        blank=True,
        verbose_name="浏览器Tab Logo地址"
    )

    enable_public_access = models.BooleanField(
        default=True,
        verbose_name="是否开启公开访问"
    )
    # API服务配置
    enable_api = models.BooleanField(
        default=True,
        verbose_name="是否开启API服务"
    )

    # 身份认证配置
    enable_auth = models.BooleanField(
        default=False,
        verbose_name="是否开启身份认证"
    )

    auth_config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="身份认证配置"
    )

    enable_cors = models.BooleanField(
        default=False,
        verbose_name="是否开启跨域设置"
    )

    cors_config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="跨域配置"
    )

    class Meta:
        db_table = "portal"