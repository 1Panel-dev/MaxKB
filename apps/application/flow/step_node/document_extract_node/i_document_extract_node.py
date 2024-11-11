# coding=utf-8

from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.util.field_message import ErrMessage


class DocumentExtractNodeSerializer(serializers.Serializer):
    # 需要查询的数据集id列表
    file_list = serializers.ListField(required=True, child=serializers.UUIDField(required=True),
                                      error_messages=ErrMessage.list("数据集id列表"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)


class IDocumentExtractNode(INode):
    type = 'document-extract-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return DocumentExtractNodeSerializer

    def _run(self):
        return self.execute(**self.flow_params_serializer.data)

    def execute(self, file_list, **kwargs) -> NodeResult:
        pass
