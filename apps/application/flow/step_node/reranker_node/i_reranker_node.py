# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： i_reranker_node.py
    @date：2024/9/4 10:40
    @desc:
"""
from typing import Type

from rest_framework import serializers

from application.flow.common import WorkflowMode
from application.flow.i_step_node import INode, NodeResult

from django.utils.translation import gettext_lazy as _


class RerankerSettingSerializer(serializers.Serializer):
    # 需要查询的条数
    top_n = serializers.IntegerField(required=True,
                                     label=_("Reference segment number"))
    # 相似度 0-1之间
    similarity = serializers.FloatField(required=True, max_value=2, min_value=0,
                                        label=_("Reference segment number"))
    max_paragraph_char_number = serializers.IntegerField(required=True,
                                                         label=_("Maximum number of words in a quoted segment"))


class RerankerStepNodeSerializer(serializers.Serializer):
    reranker_setting = RerankerSettingSerializer(required=True)

    question_reference_address = serializers.ListField(required=True)
    reranker_model_id = serializers.UUIDField(required=True)
    reranker_reference_list = serializers.ListField(required=True, child=serializers.ListField(required=True))
    show_knowledge = serializers.BooleanField(required=True,
                                              label=_("The results are displayed in the knowledge sources"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)


class IRerankerNode(INode):
    type = 'reranker-node'
    support = [WorkflowMode.APPLICATION, WorkflowMode.APPLICATION_LOOP]

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return RerankerStepNodeSerializer

    def _run(self):
        question = self.workflow_manage.get_reference_field(
            self.node_params_serializer.data.get('question_reference_address')[0],
            self.node_params_serializer.data.get('question_reference_address')[1:])
        reranker_list = [self.workflow_manage.get_reference_field(
            reference[0],
            reference[1:]) for reference in
            self.node_params_serializer.data.get('reranker_reference_list')]
        return self.execute(**self.node_params_serializer.data, question=str(question),

                            reranker_list=reranker_list)

    def execute(self, question, reranker_setting, reranker_list, reranker_model_id, show_knowledge,
                **kwargs) -> NodeResult:
        pass
