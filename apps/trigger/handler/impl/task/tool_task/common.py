# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： common.py
    @date：2026/3/27 19:54
    @desc:
"""
from abc import ABC, abstractmethod


class BaseToolTriggerTask(ABC):
    """
    任务执行器抽象
    """

    @abstractmethod
    def support(self, tool, trigger_task, **kwargs):
        pass

    @abstractmethod
    def execute(self, tool, trigger_task, **kwargs):
        pass
