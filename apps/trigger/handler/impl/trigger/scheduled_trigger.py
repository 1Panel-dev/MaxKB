# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： scheduled_trigger.py
    @date：2026/1/14 18:57
    @desc:
"""
from trigger.handler.base_trigger import BaseTrigger


class ScheduledTrigger(BaseTrigger):

    def support(self, trigger, **kwargs):
        return trigger.get('trigger_type') == 'SCHEDULED'

    def deploy(self, trigger, **kwargs):
        pass

    def undeploy(self, trigger, **kwargs):
        pass
