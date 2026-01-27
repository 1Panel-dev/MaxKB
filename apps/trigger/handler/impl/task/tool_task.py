# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_task.py
    @date：2026/1/14 19:14
    @desc:
"""

import uuid_utils.compat as uuid
from django.db.models import QuerySet

from common.utils.tool_code import ToolExecutor
from knowledge.models.knowledge_action import State
from tools.models import Tool
from trigger.handler.base_task import BaseTriggerTask
from trigger.models import TaskRecord


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


def get_tool_execute_parameters(parameter_setting, kwargs):
    parameters = {}
    for key, value in parameter_setting.items():
        parameters[key] = get_field_value(value, kwargs)
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


class ToolTask(BaseTriggerTask):
    def support(self, trigger_task, **kwargs):
        return trigger_task.get('source_type') == 'TOOL'

    def execute(self, trigger_task, **kwargs):
        parameter_setting = trigger_task.get('parameter')
        parameters = get_tool_execute_parameters(parameter_setting, kwargs)
        tool_id = trigger_task.get('source_id')
        task_record_id = uuid.uuid7()

        TaskRecord(
            id=task_record_id,
            trigger_id=trigger_task.get('trigger_id'),
            trigger_task_id=trigger_task.get('id'),
            source_type="TOOL",
            source_id=tool_id,
            task_record_id=task_record_id,
            meta={},
            state=State.STARTED
        ).save()

        try:
            tool = QuerySet(Tool).filter(id=tool_id).first()
            executor = ToolExecutor()
            # executor.exec_code(tool.code, parameters)
            print(tool)
            print(parameters)

            QuerySet(TaskRecord).filter(id=task_record_id).update(state=State.SUCCESS, run_time=0)
        except Exception as e:
            state = State.FAILURE
            QuerySet(TaskRecord).filter(id=task_record_id).update(state=state, run_time=0)
