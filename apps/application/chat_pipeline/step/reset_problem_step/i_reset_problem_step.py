# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： i_reset_problem_step.py
    @date：2024/1/9 18:12
    @desc: 重写处理问题
"""
from abc import abstractmethod
from typing import Type, List

from langchain.chat_models.base import BaseChatModel
from rest_framework import serializers

from application.chat_pipeline.I_base_chat_pipeline import IBaseChatPipelineStep
from application.chat_pipeline.pipeline_manage import PipelineManage
from application.chat_pipeline.step.chat_step.i_chat_step import ModelField
from application.models import ChatRecord
from common.field.common import InstanceField
from common.util.field_message import ErrMessage


class IResetProblemStep(IBaseChatPipelineStep):
    class InstanceSerializer(serializers.Serializer):
        # 问题文本
        problem_text = serializers.CharField(required=True, error_messages=ErrMessage.float("问题文本"))
        # 历史对答
        history_chat_record = serializers.ListField(child=InstanceField(model_type=ChatRecord, required=True),
                                                    error_messages=ErrMessage.list("历史对答"))
        # 大语言模型
        chat_model = ModelField(required=False, allow_null=True, error_messages=ErrMessage.base("大语言模型"))

    def get_step_serializer(self, manage: PipelineManage) -> Type[serializers.Serializer]:
        return self.InstanceSerializer

    def _run(self, manage: PipelineManage):
        padding_problem = self.execute(**self.context.get('step_args'))
        # 用户输入问题
        source_problem_text = self.context.get('step_args').get('problem_text')
        self.context['problem_text'] = source_problem_text
        self.context['padding_problem_text'] = padding_problem
        manage.context['problem_text'] = source_problem_text
        manage.context['padding_problem_text'] = padding_problem
        # 累加tokens
        manage.context['message_tokens'] = manage.context['message_tokens'] + self.context.get('message_tokens')
        manage.context['answer_tokens'] = manage.context['answer_tokens'] + self.context.get('answer_tokens')

    @abstractmethod
    def execute(self, problem_text: str, history_chat_record: List[ChatRecord] = None, chat_model: BaseChatModel = None,
                **kwargs):
        pass
