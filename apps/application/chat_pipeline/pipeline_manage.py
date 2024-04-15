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


class PipelineManage:
    def __init__(self, step_list: List[Type[IBaseChatPipelineStep]]):
        # 步骤执行器
        self.step_list = [step() for step in step_list]
        # 上下文
        self.context = {'message_tokens': 0, 'answer_tokens': 0}

    def run(self, context: Dict = None):
        self.context['start_time'] = time.time()
        if context is not None:
            for key, value in context.items():
                self.context[key] = value
        for step in self.step_list:
            step.run(self)

    def get_details(self):
        return reduce(lambda x, y: {**x, **y}, [{item.get('step_type'): item} for item in
                                                filter(lambda r: r is not None,
                                                       [row.get_details(self) for row in self.step_list])], {})

    class builder:
        def __init__(self):
            self.step_list: List[Type[IBaseChatPipelineStep]] = []

        def append_step(self, step: Type[IBaseChatPipelineStep]):
            self.step_list.append(step)
            return self

        def build(self):
            return PipelineManage(step_list=self.step_list)
