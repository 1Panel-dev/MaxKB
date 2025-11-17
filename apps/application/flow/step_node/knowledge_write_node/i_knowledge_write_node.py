# coding=utf-8
"""
    @project: MaxKB
    @Author：niu
    @file： i_knowledge_write_node.py
    @date：2025/11/13 11:19
    @desc:
"""
from typing import Type

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult



class KnowledgeWriteNodeParamSerializer(serializers.Serializer):
    paragraph_list = serializers.ListField(required=True, label=_("Paragraph list"))
    chunk_length = serializers.CharField(required=True, label=_("Child chunk length"))




class IKnowledgeWriteNode(INode):

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return KnowledgeWriteNodeParamSerializer


    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, paragraph_list, chunk_length, **kwargs) -> NodeResult:
        pass

    type = 'knowledge-write-node'

