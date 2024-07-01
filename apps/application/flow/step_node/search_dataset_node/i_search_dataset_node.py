# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： i_search_dataset_node.py
    @date：2024/6/3 17:52
    @desc:
"""
import re
from typing import Type

from django.core import validators
from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.util.field_message import ErrMessage


class DatasetSettingSerializer(serializers.Serializer):
    # 需要查询的条数
    top_n = serializers.IntegerField(required=True,
                                     error_messages=ErrMessage.integer("引用分段数"))
    # 相似度 0-1之间
    similarity = serializers.FloatField(required=True, max_value=2, min_value=0,
                                        error_messages=ErrMessage.float("引用分段数"))
    search_mode = serializers.CharField(required=True, validators=[
        validators.RegexValidator(regex=re.compile("^embedding|keywords|blend$"),
                                  message="类型只支持register|reset_password", code=500)
    ], error_messages=ErrMessage.char("检索模式"))
    max_paragraph_char_number = serializers.IntegerField(required=True,
                                                         error_messages=ErrMessage.float("最大引用分段字数"))


class SearchDatasetStepNodeSerializer(serializers.Serializer):
    # 需要查询的数据集id列表
    dataset_id_list = serializers.ListField(required=True, child=serializers.UUIDField(required=True),
                                            error_messages=ErrMessage.list("数据集id列表"))
    dataset_setting = DatasetSettingSerializer(required=True)

    question_reference_address = serializers.ListField(required=True, )

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)


class ISearchDatasetStepNode(INode):
    type = 'search-dataset-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return SearchDatasetStepNodeSerializer

    def _run(self):
        question = self.workflow_manage.get_reference_field(
            self.node_params_serializer.data.get('question_reference_address')[0],
            self.node_params_serializer.data.get('question_reference_address')[1:])
        return self.execute(**self.node_params_serializer.data, question=str(question), exclude_paragraph_id_list=[])

    def execute(self, dataset_id_list, dataset_setting, question,
                exclude_paragraph_id_list=None,
                **kwargs) -> NodeResult:
        pass
