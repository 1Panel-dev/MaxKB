# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： base_function_lib_node.py
    @date：2024/8/8 17:49
    @desc:
"""
import json
import time
from typing import Dict

from django.db.models import QuerySet
from django.utils.translation import gettext as _

from application.flow.i_step_node import NodeResult
from application.flow.step_node.function_lib_node.i_function_lib_node import IFunctionLibNode
from common.exception.app_exception import AppApiException
from common.util.function_code import FunctionExecutor
from common.util.rsa_util import rsa_long_decrypt
from function_lib.models.function import FunctionLib
from smartdoc.const import CONFIG

function_executor = FunctionExecutor(CONFIG.get('SANDBOX'))


def write_context(step_variable: Dict, global_variable: Dict, node, workflow):
    if step_variable is not None:
        for key in step_variable:
            node.context[key] = step_variable[key]
        if workflow.is_result(node, NodeResult(step_variable, global_variable)) and 'result' in step_variable:
            result = str(step_variable['result']) + '\n'
            yield result
            node.answer_text = result
    node.context['run_time'] = time.time() - node.context['start_time']


def get_field_value(debug_field_list, name, is_required):
    result = [field for field in debug_field_list if field.get('name') == name]
    if len(result) > 0:
        return result[-1]['value']
    if is_required:
        raise AppApiException(500, _('Field: {name} No value set').format(name=name))
    return None


def valid_reference_value(_type, value, name):
    if _type == 'int':
        instance_type = int | float
    elif _type == 'float':
        instance_type = float | int
    elif _type == 'dict':
        instance_type = dict
    elif _type == 'array':
        instance_type = list
    elif _type == 'string':
        instance_type = str
    else:
        raise Exception(_('Field: {name} Type: {_type} Value: {value} Unsupported types').format(name=name,
                                                                                                 _type=_type))
    if not isinstance(value, instance_type):
        raise Exception(
            _('Field: {name} Type: {_type} Value: {value} Type error').format(name=name, _type=_type,
                                                                              value=value))


def convert_value(name: str, value, _type, is_required, source, node):
    if not is_required and value is None:
        return None
    if not is_required and source == 'reference' and (value is None or len(value) == 0):
        return None
    if source == 'reference':
        value = node.workflow_manage.get_reference_field(
            value[0],
            value[1:])
        valid_reference_value(_type, value, name)
        if _type == 'int':
            return int(value)
        if _type == 'float':
            return float(value)
        return value
    try:
        if _type == 'int':
            return int(value)
        if _type == 'float':
            return float(value)
        if _type == 'dict':
            v = json.loads(value)
            if isinstance(v, dict):
                return v
            raise Exception(_('type error'))
        if _type == 'array':
            v = json.loads(value)
            if isinstance(v, list):
                return v
            raise Exception(_('type error'))
        return value
    except Exception as e:
        raise Exception(
            _('Field: {name} Type: {_type} Value: {value} Type error').format(name=name, _type=_type,
                                                                              value=value))


def valid_function(function_lib, user_id):
    if function_lib is None:
        raise Exception(_('Function does not exist'))
    if function_lib.permission_type == 'PRIVATE' and str(function_lib.user_id) != str(user_id):
        raise Exception(_('No permission to use this function {name}').format(name=function_lib.name))
    if not function_lib.is_active:
        raise Exception(_('Function {name} is unavailable').format(name=function_lib.name))


class BaseFunctionLibNodeNode(IFunctionLibNode):
    def save_context(self, details, workflow_manage):
        self.context['result'] = details.get('result')
        self.answer_text = str(details.get('result'))

    def execute(self, function_lib_id, input_field_list, **kwargs) -> NodeResult:
        function_lib = QuerySet(FunctionLib).filter(id=function_lib_id).first()
        valid_function(function_lib, self.flow_params_serializer.data.get('user_id'))
        params = {field.get('name'): convert_value(field.get('name'), field.get('value'), field.get('type'),
                                                   field.get('is_required'),
                                                   field.get('source'), self)
                  for field in
                  [{'value': get_field_value(input_field_list, field.get('name'), field.get('is_required'),
                                             ), **field}
                   for field in
                   function_lib.input_field_list]}

        self.context['params'] = params
        # 合并初始化参数
        if function_lib.init_params is not None:
            all_params = json.loads(rsa_long_decrypt(function_lib.init_params)) | params
        else:
            all_params = params
        result = function_executor.exec_code(function_lib.code, all_params)
        return NodeResult({'result': result}, {}, _write_context=write_context)

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            "result": self.context.get('result'),
            "params": self.context.get('params'),
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message
        }
