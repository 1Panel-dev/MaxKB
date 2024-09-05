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

from application.flow.i_step_node import INode, NodeResult
from common.util.field_message import ErrMessage


class RerankerSettingSerializer(serializers.Serializer):
    # 需要查询的条数
    top_n = serializers.IntegerField(required=True,
                                     error_messages=ErrMessage.integer("引用分段数"))
    # 相似度 0-1之间
    similarity = serializers.FloatField(required=True, max_value=2, min_value=0,
                                        error_messages=ErrMessage.float("引用分段数"))
    max_paragraph_char_number = serializers.IntegerField(required=True,
                                                         error_messages=ErrMessage.float("最大引用分段字数"))


class RerankerStepNodeSerializer(serializers.Serializer):
    reranker_setting = RerankerSettingSerializer(required=True)

    question_reference_address = serializers.ListField(required=True)
    reranker_model_id = serializers.UUIDField(required=True)
    reranker_reference_list = serializers.ListField(required=True, child=serializers.ListField(required=True))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)


class IRerankerNode(INode):
    type = 'reranker-node'

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

    def execute(self, question, reranker_setting, reranker_list, reranker_model_id,
                **kwargs) -> NodeResult:
        pass
