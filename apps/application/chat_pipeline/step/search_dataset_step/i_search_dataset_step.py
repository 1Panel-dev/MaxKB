# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： i_search_dataset_step.py
    @date：2024/1/9 18:10
    @desc: 检索知识库
"""
import re
from abc import abstractmethod
from typing import List, Type

from django.core import validators
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.chat_pipeline.I_base_chat_pipeline import IBaseChatPipelineStep, ParagraphPipelineModel
from application.chat_pipeline.pipeline_manage import PipelineManage


class ISearchDatasetStep(IBaseChatPipelineStep):
    class InstanceSerializer(serializers.Serializer):
        # 原始问题文本
        problem_text = serializers.CharField(required=True, label=_("question"))
        # 系统补全问题文本
        padding_problem_text = serializers.CharField(required=False,
                                                     label=_("System completes question text"))
        # 需要查询的数据集id列表
        knowledge_id_list = serializers.ListField(required=True, child=serializers.UUIDField(required=True),
                                                  label=_("Dataset id list"))
        # 需要排除的文档id
        exclude_document_id_list = serializers.ListField(required=True, child=serializers.UUIDField(required=True),
                                                         label=_("List of document ids to exclude"))
        # 需要排除向量id
        exclude_paragraph_id_list = serializers.ListField(required=True, child=serializers.UUIDField(required=True),
                                                          label=_("List of exclusion vector ids"))
        # 需要查询的条数
        top_n = serializers.IntegerField(required=True,
                                         label=_("Reference segment number"))
        # 相似度 0-1之间
        similarity = serializers.FloatField(required=True, max_value=1, min_value=0,
                                            label=_("Similarity"))
        search_mode = serializers.CharField(required=True, validators=[
            validators.RegexValidator(regex=re.compile("^embedding|keywords|blend$"),
                                      message=_("The type only supports embedding|keywords|blend"), code=500)
        ], label=_("Retrieval Mode"))
        workspace_id = serializers.CharField(required=True, label=_("Workspace ID"))

    def get_step_serializer(self, manage: PipelineManage) -> Type[InstanceSerializer]:
        return self.InstanceSerializer

    def _run(self, manage: PipelineManage):
        paragraph_list = self.execute(**self.context['step_args'], manage=manage)
        manage.context['paragraph_list'] = paragraph_list
        self.context['paragraph_list'] = paragraph_list

    @abstractmethod
    def execute(self, problem_text: str, knowledge_id_list: list[str], exclude_document_id_list: list[str],
                exclude_paragraph_id_list: list[str], top_n: int, similarity: float, padding_problem_text: str = None,
                search_mode: str = None,
                workspace_id=None,
                manage: PipelineManage = None,
                **kwargs) -> List[ParagraphPipelineModel]:
        """
        关于 用户和补全问题 说明: 补全问题如果有就使用补全问题去查询 反之就用用户原始问题查询
        :param similarity:                         相关性
        :param top_n:                              查询多少条
        :param problem_text:                       用户问题
        :param knowledge_id_list:                  需要查询的数据集id列表
        :param exclude_document_id_list:           需要排除的文档id
        :param exclude_paragraph_id_list:          需要排除段落id
        :param padding_problem_text                补全问题
        :param search_mode                         检索模式
        :param workspace_id                        工作空间id
        :return: 段落列表
        """
        pass
