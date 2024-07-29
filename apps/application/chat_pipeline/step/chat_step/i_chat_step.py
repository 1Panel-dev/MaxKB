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

from application.chat_pipeline.I_base_chat_pipeline import IBaseChatPipelineStep, ParagraphPipelineModel
from application.chat_pipeline.pipeline_manage import PipelineManage
from application.serializers.application_serializers import NoReferencesSetting
from common.field.common import InstanceField
from common.util.field_message import ErrMessage


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
    def handler(self, chat_id, chat_record_id, paragraph_list: List[ParagraphPipelineModel], problem_text: str,
                answer_text,
                manage, step, padding_problem_text: str = None, client_id=None, **kwargs):
        pass


class IChatStep(IBaseChatPipelineStep):
    class InstanceSerializer(serializers.Serializer):
        # 对话列表
        message_list = serializers.ListField(required=True, child=MessageField(required=True),
                                             error_messages=ErrMessage.list("对话列表"))
        model_id = serializers.UUIDField(required=False, allow_null=True, error_messages=ErrMessage.uuid("模型id"))
        # 段落列表
        paragraph_list = serializers.ListField(error_messages=ErrMessage.list("段落列表"))
        # 对话id
        chat_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("对话id"))
        # 用户问题
        problem_text = serializers.CharField(required=True, error_messages=ErrMessage.uuid("用户问题"))
        # 后置处理器
        post_response_handler = InstanceField(model_type=PostResponseHandler,
                                              error_messages=ErrMessage.base("用户问题"))
        # 补全问题
        padding_problem_text = serializers.CharField(required=False, error_messages=ErrMessage.base("补全问题"))
        # 是否使用流的形式输出
        stream = serializers.BooleanField(required=False, error_messages=ErrMessage.base("流式输出"))
        client_id = serializers.CharField(required=True, error_messages=ErrMessage.char("客户端id"))
        client_type = serializers.CharField(required=True, error_messages=ErrMessage.char("客户端类型"))
        # 未查询到引用分段
        no_references_setting = NoReferencesSetting(required=True, error_messages=ErrMessage.base("无引用分段设置"))

        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("用户id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            message_list: List = self.initial_data.get('message_list')
            for message in message_list:
                if not isinstance(message, BaseMessage):
                    raise Exception("message 类型错误")

    def get_step_serializer(self, manage: PipelineManage) -> Type[serializers.Serializer]:
        return self.InstanceSerializer

    def _run(self, manage: PipelineManage):
        chat_result = self.execute(**self.context['step_args'], manage=manage)
        manage.context['chat_result'] = chat_result

    @abstractmethod
    def execute(self, message_list: List[BaseMessage],
                chat_id, problem_text,
                post_response_handler: PostResponseHandler,
                model_id: str = None,
                user_id: str = None,
                paragraph_list=None,
                manage: PipelineManage = None,
                padding_problem_text: str = None, stream: bool = True, client_id=None, client_type=None,
                no_references_setting=None, **kwargs):
        pass
