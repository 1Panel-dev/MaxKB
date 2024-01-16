# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： i_chat_step.py
    @date：2024/1/9 18:17
    @desc: 对话
"""
from abc import abstractmethod
from typing import Type, List

from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage
from rest_framework import serializers

from application.chat_pipeline.I_base_chat_pipeline import IBaseChatPipelineStep
from application.chat_pipeline.pipeline_manage import PiplineManage
from common.field.common import InstanceField
from dataset.models import Paragraph


class ModelField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, BaseChatModel):
            self.fail('模型类型错误', value=data)
        return data

    def to_representation(self, value):
        return value


class MessageField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, BaseMessage):
            self.fail('message类型错误', value=data)
        return data

    def to_representation(self, value):
        return value


class PostResponseHandler:
    @abstractmethod
    def handler(self, chat_id, chat_record_id, paragraph_list: List[Paragraph], problem_text: str, answer_text,
                manage, step, padding_problem_text: str = None, **kwargs):
        pass


class IChatStep(IBaseChatPipelineStep):
    class InstanceSerializer(serializers.Serializer):
        # 对话列表
        message_list = serializers.ListField(required=True, child=MessageField(required=True))
        # 大语言模型
        chat_model = ModelField()
        # 段落列表
        paragraph_list = serializers.ListField()
        # 对话id
        chat_id = serializers.UUIDField(required=True)
        # 用户问题
        problem_text = serializers.CharField(required=True)
        # 后置处理器
        post_response_handler = InstanceField(model_type=PostResponseHandler)
        # 补全问题
        padding_problem_text = serializers.CharField(required=False)

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            message_list: List = self.initial_data.get('message_list')
            for message in message_list:
                if not isinstance(message, BaseMessage):
                    raise Exception("message 类型错误")

    def get_step_serializer(self, manage: PiplineManage) -> Type[serializers.Serializer]:
        return self.InstanceSerializer

    def _run(self, manage: PiplineManage):
        chat_result = self.execute(**self.context['step_args'], manage=manage)
        manage.context['chat_result'] = chat_result

    @abstractmethod
    def execute(self, message_list: List[BaseMessage],
                chat_id, problem_text,
                post_response_handler: PostResponseHandler,
                chat_model: BaseChatModel = None,
                paragraph_list=None,
                manage: PiplineManage = None,
                padding_problem_text: str = None, **kwargs):
        pass
