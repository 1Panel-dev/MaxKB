# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： __init__.py
    @date：2023/11/10 10:43
    @desc:
"""
import setting.models
from setting.models import Model
from .listener_manage import *


def run():
    listener_manage.ListenerManagement().run()
    QuerySet(Document).filter(status__in=[Status.embedding, Status.queue_up]).update(**{'status': Status.error})
    QuerySet(Model).filter(status=setting.models.Status.DOWNLOAD).update(status=setting.models.Status.ERROR,
                                                                         meta={'message': "下载程序被中断,请重试"})
