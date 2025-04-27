# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： db_model_manage.py
    @date：2024/7/22 17:00
    @desc:
"""
from importlib import import_module
from django.conf import settings


def new_instance_by_class_path(class_path: str):
    parts = class_path.rpartition('.')
    package_path = parts[0]
    class_name = parts[2]
    module = import_module(package_path)
    HandlerClass = getattr(module, class_name)
    return HandlerClass()


class DBModelManage:
    model_dict = {}

    @staticmethod
    def get_model(model_name):
        return DBModelManage.model_dict.get(model_name)

    @staticmethod
    def init():
        handles = [new_instance_by_class_path(class_path) for class_path in
                   (settings.MODEL_HANDLES if hasattr(settings, 'MODEL_HANDLES') else [])]
        for h in handles:
            model_dict = h.get_model_dict()
            DBModelManage.model_dict = {**DBModelManage.model_dict, **model_dict}
