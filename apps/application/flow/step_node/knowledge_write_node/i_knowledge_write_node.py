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

from application.flow.common import WorkflowMode
from application.flow.i_step_node import INode, NodeResult


class KnowledgeWriteNodeParamSerializer(serializers.Serializer):
    document_list = serializers.ListField(required=True, child=serializers.CharField(required=True), allow_null=True,
                                          label=_('document list'))


class IKnowledgeWriteNode(INode):

    def save_context(self, details, workflow_manage):
        pass

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return KnowledgeWriteNodeParamSerializer

    def _run(self):
        documents = self.workflow_manage.get_reference_field(
            self.node_params_serializer.data.get('document_list')[0],
            self.node_params_serializer.data.get('document_list')[1:],
        )

        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data, documents=documents)

    def execute(self, documents, **kwargs) -> NodeResult:
        pass

    type = 'knowledge-write-node'
    support = [WorkflowMode.KNOWLEDGE, WorkflowMode.KNOWLEDGE_LOOP]
