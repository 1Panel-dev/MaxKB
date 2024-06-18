# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： i_reply_node.py
    @date：2024/6/11 16:25
    @desc:
"""
from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.exception.app_exception import AppApiException
from common.util.field_message import ErrMessage


class ReplyNodeParamsSerializer(serializers.Serializer):
    reply_type = serializers.CharField(required=True, error_messages=ErrMessage.char("回复类型"))
    fields = serializers.ListField(required=False, error_messages=ErrMessage.list("引用字段"))
    content = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                    error_messages=ErrMessage.char("直接回答内容"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        if self.data.get('reply_type') == 'referencing':
            if 'fields' not in self.data:
                raise AppApiException(500, "引用字段不能为空")
            if len(self.data.get('fields')) < 2:
                raise AppApiException(500, "引用字段错误")
        else:
            if 'content' not in self.data or self.data.get('content') is None:
                raise AppApiException(500, "内容不能为空")


class IReplyNode(INode):
    type = 'reply-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return ReplyNodeParamsSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, reply_type, stream, fields=None, content=None, **kwargs) -> NodeResult:
        pass
