# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： I_base_chat_pipeline.py
    @date：2024/1/9 17:25
    @desc:
"""
import time
from abc import abstractmethod
from typing import Type

from rest_framework import serializers


class IBaseChatPipelineStep:
    def __init__(self):
        # 当前步骤上下文,用于存储当前步骤信息
        self.context = {}

    @abstractmethod
    def get_step_serializer(self, manage) -> Type[serializers.Serializer]:
        pass

    def valid_args(self, manage):
        step_serializer_clazz = self.get_step_serializer(manage)
        step_serializer = step_serializer_clazz(data=manage.context)
        step_serializer.is_valid(raise_exception=True)
        self.context['step_args'] = step_serializer.data

    def run(self, manage):
        """

        :param manage:      步骤管理器
        :return: 执行结果
        """
        start_time = time.time()
        # 校验参数,
        self.valid_args(manage)
        self._run(manage)
        self.context['start_time'] = start_time
        self.context['run_time'] = time.time() - start_time

    def _run(self, manage):
        pass

    def execute(self, **kwargs):
        pass

    def get_details(self, manage, **kwargs):
        """
        运行详情
        :return: 步骤详情
        """
        return None
