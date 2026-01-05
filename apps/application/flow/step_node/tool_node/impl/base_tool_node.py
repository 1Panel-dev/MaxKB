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

from django.utils.translation import gettext as _

from application.flow.i_step_node import NodeResult
from application.flow.step_node.tool_node.i_tool_node import IToolNode
from common.utils.tool_code import ToolExecutor
from maxkb.const import CONFIG

function_executor = ToolExecutor()


def write_context(step_variable: Dict, global_variable: Dict, node, workflow):
    if step_variable is not None:
        for key in step_variable:
            node.context[key] = step_variable[key]
        if workflow.is_result(node, NodeResult(step_variable, global_variable)) and 'result' in step_variable:
            result = str(step_variable['result']) + '\n'
            yield result
            node.answer_text = result
    node.context['run_time'] = time.time() - node.context['start_time']


def valid_reference_value(_type, value, name):
    try:
        if _type == 'int':
            instance_type = int | float
        elif _type == 'boolean':
            instance_type = bool
        elif _type == 'float':
            instance_type = float | int
        elif _type == 'dict':
            value = json.loads(value) if isinstance(value, str) else value
            instance_type = dict
        elif _type == 'array':
            value = json.loads(value) if isinstance(value, str) else value
            instance_type = list
        elif _type == 'string':
            instance_type = str
        else:
            raise Exception(_(
                'Field: {name} Type: {_type} Value: {value} Unsupported types'
            ).format(name=name, _type=_type))
    except:
        return value
    if not isinstance(value, instance_type):
        raise Exception(_(
            'Field: {name} Type: {_type} Value: {value} Type error'
        ).format(name=name, _type=_type, value=value))
    return value


def convert_value(name: str, value, _type, is_required, source, node):
    if not is_required and (value is None or ((isinstance(value, str) or isinstance(value, list)) and len(value) == 0)):
        return None
    if source == 'reference':
        value = node.workflow_manage.get_reference_field(
            value[0],
            value[1:])
        if value is None:
            if not is_required:
                return None
            else:
                raise Exception(_(
                    'Field: {name} Type: {_type} is required'
                ).format(name=name, _type=_type))
        value = valid_reference_value(_type, value, name)
        if _type == 'int':
            return int(value)
        if _type == 'float':
            return float(value)
        return value
    try:
        value = node.workflow_manage.generate_prompt(value)
        if _type == 'int':
            return int(value)
        if _type == 'boolean':
            value = 0 if ['0', '[]'].__contains__(value) else value
            return bool(value)
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


class BaseToolNodeNode(IToolNode):
    def save_context(self, details, workflow_manage):
        self.context['result'] = details.get('result')
        self.context['exception_message'] = details.get('err_message')
        if self.node_params.get('is_result', False):
            self.answer_text = str(details.get('result'))

    def execute(self, input_field_list, code, **kwargs) -> NodeResult:
        params = {field.get('name'): convert_value(field.get('name'), field.get('value'), field.get('type'),
                                                   field.get('is_required'), field.get('source'), self)
                  for field in input_field_list}
        result = function_executor.exec_code(code, params)
        self.context['params'] = params
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
            'err_message': self.err_message,
            'enableException': self.node.properties.get('enableException'),
        }
