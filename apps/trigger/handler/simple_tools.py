# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： simple_task.py
    @date：2026/1/14 19:18
    @desc:
"""
from trigger.handler.impl.task.application_task import ApplicationTask
from trigger.handler.impl.trigger.scheduled_trigger import ScheduledTrigger

simple_task_handlers = [ApplicationTask()]

simple_trigger_handlers = [ScheduledTrigger()]


def execute(trigger_task, **kwargs):
    """
    执行触发器任务
    @param trigger_task:  触发器任务数据
    @param kwargs:        额外数据
    @return:
    """
    for simple_task_handler in simple_task_handlers:
        if simple_task_handler.support(trigger_task, **kwargs):
            return simple_task_handler.execute(trigger_task, **kwargs)
    raise Exception("不支持的处理器类型")


def deploy(trigger, **kwargs):
    """
    部署触发器
    @param trigger: 触发器字典数据
    @param kwargs:  额外数据
    @return:
    """
    for simple_trigger_handler in simple_trigger_handlers:
        if simple_trigger_handler.support(trigger, **kwargs):
            return simple_trigger_handler.deploy(trigger, **kwargs)
    raise Exception("不支持的触发器类型")


def undeploy(trigger, **kwargs):
    """
    取消部署触发器
    @param trigger: 触发器字典数据
    @param kwargs:  额外数据
    @return:
    """
    for simple_trigger_handler in simple_trigger_handlers:
        if simple_trigger_handler.support(trigger, **kwargs):
            return simple_trigger_handler.undeploy(trigger, **kwargs)
    raise Exception("不支持的触发器类型")
