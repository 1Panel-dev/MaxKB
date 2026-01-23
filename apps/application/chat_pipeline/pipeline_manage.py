# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： pipeline_manage.py
    @date：2024/1/9 17:40
    @desc:
"""
import time
from functools import reduce
from typing import List, Type, Dict

from application.chat_pipeline.I_base_chat_pipeline import IBaseChatPipelineStep
from common.handle.base_to_response import BaseToResponse
from common.handle.impl.response.system_to_response import SystemToResponse


class PipelineManage:
    def __init__(self, step_list: List[Type[IBaseChatPipelineStep]],
                 base_to_response: BaseToResponse = SystemToResponse(),
                 debug=False):
        # 步骤执行器
        self.step_list = [step() for step in step_list]
        self.run_step_list = []
        # 上下文
        self.context = {'message_tokens': 0, 'answer_tokens': 0}
        self.base_to_response = base_to_response
        self.debug = debug

    def run(self, context: Dict = None):
        self.context['start_time'] = time.time()
        if context is not None:
            for key, value in context.items():
                self.context[key] = value
        for step in self.step_list:
            self.run_step_list.append(step)
            step.run(self)

    def get_details(self):
        return reduce(lambda x, y: {**x, **y}, [{item.get('step_type'): item} for item in
                                                filter(lambda r: r is not None,
                                                       [row.get_details(self) for row in self.run_step_list])], {})

    def get_base_to_response(self):
        return self.base_to_response

    class builder:
        def __init__(self):
            self.step_list: List[Type[IBaseChatPipelineStep]] = []
            self.base_to_response = SystemToResponse()
            self.debug = False

        def append_step(self, step: Type[IBaseChatPipelineStep]):
            self.step_list.append(step)
            return self

        def add_base_to_response(self, base_to_response: BaseToResponse):
            self.base_to_response = base_to_response
            return self

        def add_debug(self, debug):
            self.debug = debug
            return self

        def build(self):
            return PipelineManage(step_list=self.step_list, base_to_response=self.base_to_response, debug=self.debug)
