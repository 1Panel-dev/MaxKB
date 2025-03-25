# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： common.py
    @date：2025/3/25 17:27
    @desc:
"""
from django.db.models import QuerySet

from function_lib.models.function import FunctionLib


def get_function_lib_operation_object(function_lib_id):
    function_lib_model = QuerySet(model=FunctionLib).filter(id=function_lib_id).first()
    if function_lib_model is not None:
        return {
            "name": function_lib_model.name
        }
    return {}
