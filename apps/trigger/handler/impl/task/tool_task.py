# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_task.py
    @date：2026/1/14 19:14
    @desc:
"""
import json
import time
import traceback

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.utils.translation import gettext as _

from common.utils.logger import maxkb_logger
from common.utils.rsa_util import rsa_long_decrypt
from common.utils.tool_code import ToolExecutor
from knowledge.models.knowledge_action import State
from tools.models import Tool, ToolRecord, ToolTaskTypeChoices
from trigger.handler.base_task import BaseTriggerTask
from trigger.models import TaskRecord

executor = ToolExecutor()


def get_reference(fields, obj):
    for field in fields:
        value = obj.get(field)
        if value is None:
            return None
        else:
            obj = value
    return obj


def get_field_value(value, kwargs):
    source = value.get('source')
    if source == 'custom':
        return value.get('value')
    else:
        return get_reference(value.get('value'), kwargs)


def _convert_value(_type, value):
    if value is None:
        return None

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


def get_tool_execute_parameters(input_field_list, parameter_setting, kwargs):
    type_map = {f.get("name"): f.get("type") for f in (input_field_list or []) if f.get("name")}

    parameters = {}
    for key, value in parameter_setting.items():
        raw = get_field_value(value, kwargs)
        parameters[key] = _convert_value(type_map.get(key), raw)
    return parameters


def get_loop_workflow_node(node_list):
    result = []
    for item in node_list:
        if item.get('type') == 'loop-node':
            for loop_item in item.get('loop_node_data') or []:
                for inner_item in loop_item.values():
                    result.append(inner_item)
    return result


def get_workflow_state(details):
    node_list = details.values()
    all_node = [*node_list, *get_loop_workflow_node(node_list)]
    err = any([True for value in all_node if value.get('status') == 500 and not value.get('enableException')])
    if err:
        return State.FAILURE
    return State.SUCCESS


def _get_result_detail(result):
    if isinstance(result, dict):
        result_dict = {k: (str(v)[:500] if len(str(v)) > 500 else v) for k, v in result.items()}
    elif isinstance(result, list):
        result_dict = [str(item)[:500] if len(str(item)) > 500 else item for item in result]
    elif isinstance(result, str):
        result_dict = result[:500] if len(result) > 500 else result
    else:
        result_dict = result
    return result_dict


class ToolTask(BaseTriggerTask):
    def support(self, trigger_task, **kwargs):
        return trigger_task.get('source_type') == 'TOOL'

    def execute(self, trigger_task, **kwargs):
        parameter_setting = trigger_task.get('parameter')
        tool_id = trigger_task.get('source_id')
        task_record_id = uuid.uuid7()
        start_time = time.time()
        try:
            tool = QuerySet(Tool).filter(id=tool_id, is_active=True).first()
            if not tool:
                maxkb_logger.info(f"Tool with id {tool_id} not found or inactive.")
                return

            TaskRecord(
                id=task_record_id,
                trigger_id=trigger_task.get('trigger'),
                trigger_task_id=trigger_task.get('id'),
                source_type="TOOL",
                source_id=tool_id,
                task_record_id=task_record_id,
                meta={'input': parameter_setting, 'output': {}},
                state=State.STARTED
            ).save()
            ToolRecord(
                id=task_record_id,
                workspace_id=tool.workspace_id,
                tool_id=tool.id,
                source_type=ToolTaskTypeChoices.TRIGGER,
                source_id=trigger_task.get('trigger'),
                meta={'input': parameter_setting, 'output': {}},
                state=State.STARTED
            ).save()

            parameters = get_tool_execute_parameters(tool.input_field_list, parameter_setting, kwargs)
            init_params_default_value = {i["field"]: i.get('default_value') for i in tool.init_field_list}

            if tool.init_params is not None:
                parameters = json.loads(rsa_long_decrypt(tool.init_params)) | parameters
            all_params = init_params_default_value | parameters
            result = executor.exec_code(tool.code, all_params)

            result_dict = _get_result_detail(result)

            maxkb_logger.debug(f"Tool execution result: {result}")

            QuerySet(TaskRecord).filter(id=task_record_id).update(
                state=State.SUCCESS,
                run_time=time.time() - start_time,
                meta={'input': parameter_setting, 'output': result_dict}
            )
            QuerySet(ToolRecord).filter(id=task_record_id).update(
                state=State.SUCCESS,
                run_time=time.time() - start_time,
                meta={'input': parameters, 'output': result_dict}
            )
        except Exception as e:
            maxkb_logger.error(f"Tool execution error: {traceback.format_exc()}")
            QuerySet(TaskRecord).filter(id=task_record_id).update(
                state=State.FAILURE,
                run_time=time.time() - start_time,
                meta={'input': parameter_setting, 'output': 'Error: ' + str(e), 'err_message': 'Error: ' + str(e)}
            )
            QuerySet(ToolRecord).filter(id=task_record_id).update(
                state=State.FAILURE,
                run_time=time.time() - start_time,
                meta={'input': parameter_setting, 'output': 'Error: ' + str(e), 'err_message': 'Error: ' + str(e)}
            )
