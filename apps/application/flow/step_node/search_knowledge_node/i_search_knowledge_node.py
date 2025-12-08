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
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.utils.common import flat_map


class DatasetSettingSerializer(serializers.Serializer):
    # 需要查询的条数
    top_n = serializers.IntegerField(required=True,
                                     label=_("Reference segment number"))
    # 相似度 0-1之间
    similarity = serializers.FloatField(required=True, max_value=2, min_value=0,
                                        label=_('similarity'))
    search_mode = serializers.CharField(required=True, validators=[
        validators.RegexValidator(regex=re.compile("^embedding|keywords|blend$"),
                                  message=_("The type only supports embedding|keywords|blend"), code=500)
    ], label=_("Retrieval Mode"))
    max_paragraph_char_number = serializers.IntegerField(required=True,
                                                         label=_("Maximum number of words in a quoted segment"))


class SearchDatasetStepNodeSerializer(serializers.Serializer):
    # 需要查询的数据集id列表
    knowledge_id_list = serializers.ListField(required=True, child=serializers.UUIDField(required=True),
                                              label=_("Dataset id list"))
    knowledge_setting = DatasetSettingSerializer(required=True)

    question_reference_address = serializers.ListField(required=True)

    show_knowledge = serializers.BooleanField(required=True,
                                              label=_("The results are displayed in the knowledge sources"))
    search_scope_type = serializers.ChoiceField(
        required=False, choices=['custom', 'referencing'], label=_("search scope type"),
        allow_null=True, default='custom'
    )
    search_scope_source = serializers.ChoiceField(
        required=False, choices=['document', 'knowledge'],
        label=_("search scope variable type"), default='knowledge'
    )
    search_scope_reference = serializers.ListField(
        required=False, label=_("search scope variable"), default=list
    )

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)


def get_paragraph_list(chat_record, node_id):
    return flat_map([chat_record.details[key].get('paragraph_list', []) for key in chat_record.details if
                     (chat_record.details[
                          key].get('type', '') == 'search-dataset-node') and chat_record.details[key].get(
                         'paragraph_list', []) is not None and key == node_id])


class ISearchKnowledgeStepNode(INode):
    type = 'search-knowledge-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return SearchDatasetStepNodeSerializer

    def _run(self):
        question = self.workflow_manage.get_reference_field(
            self.node_params_serializer.data.get('question_reference_address')[0],
            self.node_params_serializer.data.get('question_reference_address')[1:])
        exclude_paragraph_id_list = []
        if self.flow_params_serializer.data.get('re_chat', False):
            history_chat_record = self.flow_params_serializer.data.get('history_chat_record', [])
            paragraph_id_list = [p.get('id') for p in flat_map(
                [get_paragraph_list(chat_record, self.runtime_node_id) for chat_record in history_chat_record if
                 chat_record.problem_text == question])]
            exclude_paragraph_id_list = list(set(paragraph_id_list))

        return self.execute(**self.node_params_serializer.data, question=str(question),
                            exclude_paragraph_id_list=exclude_paragraph_id_list)

    def execute(self, dataset_id_list, dataset_setting, question, show_knowledge, search_scope_type,
                search_scope_source,
                search_scope_reference,
                exclude_paragraph_id_list=None,
                **kwargs) -> NodeResult:
        pass
