# coding=utf-8

from typing import Type

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.util.field_message import ErrMessage


class DocumentExtractNodeSerializer(serializers.Serializer):
    document_list = serializers.ListField(required=False, error_messages=ErrMessage.list(_("document")))


class IDocumentExtractNode(INode):
    type = 'document-extract-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return DocumentExtractNodeSerializer

    def _run(self):
        res = self.workflow_manage.get_reference_field(self.node_params_serializer.data.get('document_list')[0],
                                                       self.node_params_serializer.data.get('document_list')[1:])
        return self.execute(document=res, **self.flow_params_serializer.data)

    def execute(self, document, chat_id, **kwargs) -> NodeResult:
        pass
