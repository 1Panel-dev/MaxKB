# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_task.py
    @date：2026/1/14 19:14
    @desc:
"""
from trigger.handler.base_task import BaseTriggerTask


class ApplicationTask(BaseTriggerTask):
    def support(self, trigger_task, **kwargs):
        return trigger_task.get('source_type') == 'APPLICATION'

    def execute(self, trigger_task, **kwargs):
        pass
