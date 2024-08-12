# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： base_function_lib_node.py
    @date：2024/8/8 17:49
    @desc:
"""
import json
import os

from django.db.models import QuerySet

from application.flow.i_step_node import NodeResult
from application.flow.step_node.function_lib_node.i_function_lib_node import IFunctionLibNode
from common.exception.app_exception import AppApiException
from common.util.function_code import FunctionExecutor
from function_lib.models.function import FunctionLib
from smartdoc.const import PROJECT_DIR

function_executor = FunctionExecutor(os.path.join(PROJECT_DIR, 'data', 'result', "function_node"))


def get_field_value(debug_field_list, name, is_required):
    result = [field for field in debug_field_list if field.get('name') == name]
    if len(result) > 0:
        return result[-1]
    if is_required:
        raise AppApiException(500, f"{name}字段未设置值")
    return None


def convert_value(name: str, value: str, _type):
    try:
        if _type == 'int':
            return int(value)
        if _type == 'float':
            return float(value)
        if _type == 'dict':
            return json.loads(value)
        if _type == 'array':
            return json.loads(value)
        return value
    except Exception as e:
        raise AppApiException(500, f'字段:{name}类型:{_type}值:{value}类型转换错误')


class BaseFunctionLibNodeNode(IFunctionLibNode):
    def execute(self, function_lib_id, input_field_list, **kwargs) -> NodeResult:
        function_lib = QuerySet(FunctionLib).filter(id=function_lib_id).first()
        params = {field.get('name'): convert_value(field.get('name'), field.get('value'), field.get('type'))
                  for field in
                  [{'value': get_field_value(input_field_list, field.get('name'), field.get('is_required')), **field}
                   for field in
                   function_lib.input_field_list]}
        result = function_executor.exec_code(function_lib.code, params)
        return NodeResult({'result': result}, {})
