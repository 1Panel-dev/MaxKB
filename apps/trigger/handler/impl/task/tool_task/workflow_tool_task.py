# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： workflow_tool_task.py.py
    @date：2026/3/27 18:47
    @desc:
"""
import json
import time
import traceback

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.utils.translation import gettext as _

from application.flow.common import WorkflowMode, Workflow
from application.flow.i_step_node import ToolWorkflowPostHandler, get_tool_workflow_state
from application.serializers.common import ToolExecute
from common.utils.logger import maxkb_logger
from common.utils.tool_code import ToolExecutor
from knowledge.models.knowledge_action import State
from tools.models import ToolRecord, ToolTaskTypeChoices, ToolWorkflowVersion, ToolType
from trigger.handler.impl.task.tool_task.common import BaseToolTriggerTask
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


class ToolTask(BaseToolTriggerTask):
    def support(self, tool, trigger_task, **kwargs):
        return tool.tool_type == ToolType.WORKFLOW

    def execute(self, tool, trigger_task, **kwargs):
        parameter_setting = trigger_task.get('parameter')
        tool_id = trigger_task.get('source_id')
        task_record_id = uuid.uuid7()
        start_time = time.time()
        try:
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
            tool_workflow_version = QuerySet(ToolWorkflowVersion).filter(tool_id=tool.id).order_by(
                '-create_time')[0:1].first()
            if not tool_workflow_version:
                maxkb_logger.info(f"Tool with id {tool_id} not found or inactive.")
                return
            flow = Workflow.new_instance(tool_workflow_version.work_flow, WorkflowMode.TOOL)
            base_node = flow.get_node('tool-base-node')
            user_input_field_list = base_node.properties.get("user_input_field_list") or []
            parameters = get_tool_execute_parameters(user_input_field_list,
                                                     parameter_setting.get('user_input_field_list'), kwargs)
            took_execute = ToolExecute(tool_id, str(task_record_id),
                                       tool.workspace_id,
                                       ToolTaskTypeChoices.TRIGGER,
                                       trigger_task.get('trigger'),
                                       False)
            from application.flow.tool_workflow_manage import ToolWorkflowManage
            work_flow_manage = ToolWorkflowManage(
                flow,
                {
                    'chat_record_id': task_record_id,
                    'tool_id': tool_id,
                    'stream': True,
                    'workspace_id': tool.workspace_id,
                    **parameters},
                ToolWorkflowPostHandler(took_execute, tool_id),
                is_the_task_interrupted=lambda: False,
                child_node=None,
                start_node_id=None,
                start_node_data=None,
                chat_record=None
            )
            res = work_flow_manage.run()
            for r in res:
                pass
            state = get_tool_workflow_state(work_flow_manage)
            QuerySet(TaskRecord).filter(id=task_record_id).update(
                state=state,
                run_time=time.time() - start_time,
                meta={'input': parameter_setting, 'output': work_flow_manage.out_context}
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
