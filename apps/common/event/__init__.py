# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： __init__.py
    @date：2023/11/10 10:43
    @desc:
"""
from .listener_manage import *


def run():
    listener_manage.ListenerManagement().run()
    QuerySet(Document).filter(status=Status.embedding).update(**{'status': Status.error})
