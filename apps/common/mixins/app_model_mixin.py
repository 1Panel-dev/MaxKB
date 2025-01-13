# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： app_model_mixin.py
    @date：2023/9/21 9:41
    @desc:
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

class AppModelMixin(models.Model):
    create_time = models.DateTimeField(verbose_name=_('Create time'), auto_now_add=True)
    update_time = models.DateTimeField(verbose_name=_('Update time'), auto_now=True)

    class Meta:
        abstract = True
        ordering = ['create_time']
