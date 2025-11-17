# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： i_data_source_local_node.py
    @date：2025/11/11 10:06
    @desc:
"""
from abc import abstractmethod
from typing import Type

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.common import WorkflowMode
from application.flow.i_step_node import INode, NodeResult


class DataSourceLocalNodeParamsSerializer(serializers.Serializer):
    file_type_list = serializers.ListField(child=serializers.CharField(label=('')), label='')
    file_size_limit = serializers.IntegerField(required=True, label=_("Number of uploaded files"))
    file_count_limit = serializers.IntegerField(required=True, label=_("Upload file size"))


class IDataSourceLocalNode(INode):
    type = 'data-source-local-node'

    @staticmethod
    @abstractmethod
    def get_form_list(node):
        pass

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return DataSourceLocalNodeParamsSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, file_type_list, file_size_limit, file_count_limit, **kwargs) -> NodeResult:
        pass

    support = [WorkflowMode.KNOWLEDGE]
