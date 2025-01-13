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

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.chat_pipeline.I_base_chat_pipeline import IBaseChatPipelineStep
from application.chat_pipeline.pipeline_manage import PipelineManage
from application.models import ChatRecord
from common.field.common import InstanceField
from common.util.field_message import ErrMessage


class IResetProblemStep(IBaseChatPipelineStep):
    class InstanceSerializer(serializers.Serializer):
        # 问题文本
        problem_text = serializers.CharField(required=True, error_messages=ErrMessage.float(_("question")))
        # 历史对答
        history_chat_record = serializers.ListField(child=InstanceField(model_type=ChatRecord, required=True),
                                                    error_messages=ErrMessage.list(_("History Questions")))
        # 大语言模型
        model_id = serializers.UUIDField(required=False, allow_null=True, error_messages=ErrMessage.uuid(_("Model id")))
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_("User ID")))
        problem_optimization_prompt = serializers.CharField(required=False, max_length=102400,
                                                            error_messages=ErrMessage.char(
                                                                _("Question completion prompt")))

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
        manage.context['message_tokens'] = manage.context.get('message_tokens', 0) + self.context.get('message_tokens',
                                                                                                      0)
        manage.context['answer_tokens'] = manage.context.get('answer_tokens', 0) + self.context.get('answer_tokens', 0)

    @abstractmethod
    def execute(self, problem_text: str, history_chat_record: List[ChatRecord] = None, model_id: str = None,
                problem_optimization_prompt=None,
                user_id=None,
                **kwargs):
        pass
