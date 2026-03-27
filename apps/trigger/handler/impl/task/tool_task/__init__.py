# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： __init__.py.py
    @date：2026/3/27 18:45
    @desc:
"""
from .base_tool_task import ToolTask as BaseToolTask
from .workflow_tool_task import ToolTask as WorkflowToolTask
from django.db.models import QuerySet

from common.utils.logger import maxkb_logger
from tools.models import Tool
from trigger.handler.base_task import BaseTriggerTask

TOOL_TASKS = [BaseToolTask(), WorkflowToolTask()]


def execute(tool, trigger_task, **kwargs):
    for TOOL_TASK in TOOL_TASKS:
        if TOOL_TASK.support(tool, trigger_task, **kwargs):
            TOOL_TASK.execute(tool, trigger_task, **kwargs)


class ToolTask(BaseTriggerTask):
    def support(self, trigger_task, **kwargs):
        return trigger_task.get('source_type') == 'TOOL'

    def execute(self, trigger_task, **kwargs):
        tool_id = trigger_task.get('source_id')
        tool = QuerySet(Tool).filter(id=tool_id, is_active=True).first()
        if not tool:
            maxkb_logger.info(f"Tool with id {tool_id} not found or inactive.")
            return
        execute(tool, trigger_task, **kwargs)
