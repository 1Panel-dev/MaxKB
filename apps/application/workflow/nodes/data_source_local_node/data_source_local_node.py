# coding=utf-8
"""
@project: MaxKB
@Author:  虎虎虎
@file:    data_source_local_node.py
@date:    2026/9/11
@desc:    本地文件数据源节点：知识库工作流的起始节点之一，把上传的文件列表写入节点输出供下游读取
"""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode


class DataSourceLocalNodeParamsSerializer(serializers.Serializer):
    file_type_list = serializers.ListField(child=serializers.CharField(label=_("")), label=_(""))
    file_size_limit = serializers.IntegerField(required=True, label=_("Upload file size"))
    file_count_limit = serializers.IntegerField(required=True, label=_("Number of uploaded files"))


class DataSourceLocalNode(INode):
    serializer_class = DataSourceLocalNodeParamsSerializer
    supported_workflow_type_list = [WorkflowType.KNOWLEDGE]
    type = "data-source-local-node"

    @staticmethod
    def get_form_list(node):
        node_data = node.get("properties").get("node_data")
        return [
            {
                "field": "file_list",
                "input_type": "LocalFileUpload",
                "attrs": {
                    "file_count_limit": node_data.get("file_count_limit") or 10,
                    "file_size_limit": node_data.get("file_size_limit") or 100,
                    "file_type_list": node_data.get("file_type_list"),
                },
                "label": "",
            }
        ]

    def execute(self):
        # 文件列表来自工作流入参 data_source.file_list，写入本节点输出供下游节点引用
        workflow_params = self.get_workflow_parameters()
        file_list = (workflow_params.get("data_source") or {}).get("file_list")
        self.write_context("file_list", file_list)

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "file_list": self.get_context("file_list"),
                "knowledge_base": self.get_workflow_parameters().get("knowledge_base"),
                "enableException": self.node.properties.get("enableException"),
            }
        )
        return details
