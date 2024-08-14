# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： base_function_lib_node.py
    @date：2024/8/8 17:49
    @desc:
"""
import json

from application.flow.i_step_node import NodeResult
from application.flow.step_node.function_node.i_function_node import IFunctionNode
from common.exception.app_exception import AppApiException
from common.util.function_code import FunctionExecutor
from smartdoc.const import CONFIG

function_executor = FunctionExecutor(CONFIG.get('SANDBOX'))


def convert_value(name: str, value: str, _type, is_required: bool):
    if not is_required and value is None:
        return None
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


class BaseFunctionNodeNode(IFunctionNode):
    def execute(self, input_field_list, code, **kwargs) -> NodeResult:
        params = {field.get('name'): convert_value(field.get('name'), field.get('value'), field.get('type'),
                                                   field.get('is_required'))
                  for field in input_field_list}
        result = function_executor.exec_code(code, params)
        return NodeResult({'result': result}, {})
