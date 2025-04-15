# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： database_model_manage.py
    @date：2025/4/15 11:06
    @desc:
"""
from importlib import import_module
from django.conf import settings


def new_instance_by_class_path(class_path: str):
    """
    根据class_path 创建实例
    """
    parts = class_path.rpartition('.')
    package_path = parts[0]
    class_name = parts[2]
    module = import_module(package_path)
    HandlerClass = getattr(module, class_name)
    return HandlerClass()


class DatabaseModelManage:
    """
    模型字典
    """
    model_dict = {}

    @staticmethod
    def get_model(model_name):
        """
        根据模型
        """
        return DatabaseModelManage.model_dict.get(model_name)

    @staticmethod
    def init():
        handles = [new_instance_by_class_path(class_path) for class_path in
                   (settings.MODEL_HANDLES if hasattr(settings, 'MODEL_HANDLES') else [])]
        for h in handles:
            model_dict = h.get_model_dict()
            DatabaseModelManage.model_dict = {**DatabaseModelManage.model_dict, **model_dict}
