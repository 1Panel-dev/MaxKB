# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： i_generate_human_message_step.py
    @date：2024/1/9 18:15
    @desc: 生成对话模板
"""
from abc import abstractmethod
from typing import Type, List

from langchain.schema import BaseMessage
from rest_framework import serializers

from application.chat_pipeline.I_base_chat_pipeline import IBaseChatPipelineStep, ParagraphPipelineModel
from application.chat_pipeline.pipeline_manage import PipelineManage
from application.models import ChatRecord
from application.serializers.application_serializers import NoReferencesSetting
from common.field.common import InstanceField
from common.util.field_message import ErrMessage


class IGenerateHumanMessageStep(IBaseChatPipelineStep):
    class InstanceSerializer(serializers.Serializer):
        # 问题
        problem_text = serializers.CharField(required=True, error_messages=ErrMessage.char("问题"))
        # 段落列表
        paragraph_list = serializers.ListField(child=InstanceField(model_type=ParagraphPipelineModel, required=True),
                                               error_messages=ErrMessage.list("段落列表"))
        # 历史对答
        history_chat_record = serializers.ListField(child=InstanceField(model_type=ChatRecord, required=True),
                                                    error_messages=ErrMessage.list("历史对答"))
        # 多轮对话数量
        dialogue_number = serializers.IntegerField(required=True, error_messages=ErrMessage.integer("多轮对话数量"))
        # 最大携带知识库段落长度
        max_paragraph_char_number = serializers.IntegerField(required=True, error_messages=ErrMessage.integer(
            "最大携带知识库段落长度"))
        # 模板
        prompt = serializers.CharField(required=True, error_messages=ErrMessage.char("提示词"))
        # 补齐问题
        padding_problem_text = serializers.CharField(required=False, error_messages=ErrMessage.char("补齐问题"))
        # 未查询到引用分段
        no_references_setting = NoReferencesSetting(required=True, error_messages=ErrMessage.base("无引用分段设置"))

    def get_step_serializer(self, manage: PipelineManage) -> Type[serializers.Serializer]:
        return self.InstanceSerializer

    def _run(self, manage: PipelineManage):
        message_list = self.execute(**self.context['step_args'])
        manage.context['message_list'] = message_list

    @abstractmethod
    def execute(self,
                problem_text: str,
                paragraph_list: List[ParagraphPipelineModel],
                history_chat_record: List[ChatRecord],
                dialogue_number: int,
                max_paragraph_char_number: int,
                prompt: str,
                padding_problem_text: str = None,
                no_references_setting=None,
                **kwargs) -> List[BaseMessage]:
        """

        :param problem_text:               原始问题文本
        :param paragraph_list:             段落列表
        :param history_chat_record:        历史对话记录
        :param dialogue_number:            多轮对话数量
        :param max_paragraph_char_number:  最大段落长度
        :param prompt:                     模板
        :param padding_problem_text        用户修改文本
        :param kwargs:                     其他参数
        :param no_references_setting:     无引用分段设置
        :return:
        """
        pass
