# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： app_model_mixin.py
    @date：2023/9/21 9:41
    @desc:
"""
from django.db import models


class AppModelMixin(models.Model):
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="修改时间", auto_now=True)

    class Meta:
        abstract = True
        ordering = ['create_time']
