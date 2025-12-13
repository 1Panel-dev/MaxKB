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

from application.flow.common import WorkflowMode
from application.flow.i_step_node import INode, NodeResult
from common.exception.app_exception import AppApiException

from django.utils.translation import gettext_lazy as _


class ReplyNodeParamsSerializer(serializers.Serializer):
    reply_type = serializers.CharField(required=True, label=_("Response Type"))
    fields = serializers.ListField(required=False, label=_("Reference Field"))
    content = serializers.CharField(required=False, allow_blank=True, allow_null=True,
                                    label=_("Direct answer content"))
    is_result = serializers.BooleanField(required=False,
                                         label=_('Whether to return content'))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        if self.data.get('reply_type') == 'referencing':
            if 'fields' not in self.data:
                raise AppApiException(500, _("Reference field cannot be empty"))
            if len(self.data.get('fields')) < 2:
                raise AppApiException(500, _("Reference field error"))
        else:
            if 'content' not in self.data or self.data.get('content') is None:
                raise AppApiException(500, _("Content cannot be empty"))


class IReplyNode(INode):
    type = 'reply-node'
    support = [WorkflowMode.APPLICATION, WorkflowMode.APPLICATION_LOOP, WorkflowMode.KNOWLEDGE_LOOP,
               WorkflowMode.KNOWLEDGE]

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return ReplyNodeParamsSerializer

    def _run(self):
        if [WorkflowMode.KNOWLEDGE, WorkflowMode.KNOWLEDGE_LOOP].__contains__(
                self.workflow_manage.flow.workflow_mode):
            return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data,
                                **{'stream': True})
        else:
            return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, reply_type, stream, fields=None, content=None, **kwargs) -> NodeResult:
        pass
