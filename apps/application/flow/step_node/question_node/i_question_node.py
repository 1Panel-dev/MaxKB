# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： i_chat_node.py
    @date：2024/6/4 13:58
    @desc:
"""
from typing import Type

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.common import WorkflowMode
from application.flow.i_step_node import INode, NodeResult


class QuestionNodeSerializer(serializers.Serializer):
    model_id = serializers.CharField(required=True, label=_("Model id"))
    system = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                   label=_("Role Setting"))
    prompt = serializers.CharField(required=True, label=_("Prompt word"))
    # 多轮对话数量
    dialogue_number = serializers.IntegerField(required=True, label=
    _("Number of multi-round conversations"))

    is_result = serializers.BooleanField(required=False,
                                         label=_('Whether to return content'))
    model_params_setting = serializers.DictField(required=False,
                                                 label=_("Model parameter settings"))


class IQuestionNode(INode):
    type = 'question-node'
    support = [WorkflowMode.APPLICATION, WorkflowMode.APPLICATION_LOOP, WorkflowMode.KNOWLEDGE,
               WorkflowMode.KNOWLEDGE_LOOP]

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return QuestionNodeSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, model_id, system, prompt, dialogue_number, history_chat_record, stream, chat_id, chat_record_id,
                model_params_setting=None,
                **kwargs) -> NodeResult:
        pass
