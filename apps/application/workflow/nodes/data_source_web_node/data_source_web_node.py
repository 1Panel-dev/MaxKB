# coding=utf-8
"""
@project: MaxKB
@Author:  虎虎虎
@file:    data_source_web_node.py
@date:    2026/9/16
@desc:    Web 站点数据源节点：知识库工作流的起始节点之一，按根地址抓取站点内容写入 document_list 供下游读取
"""

import traceback

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import CancelledException, INode
from common.utils.fork import ChildLink, Fork, ForkManage
from common.utils.logger import maxkb_logger


class DataSourceWebNodeParamsSerializer(serializers.Serializer):
    source_url = serializers.CharField(required=True, label=_("Web source url"))
    selector = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, label=_("Web knowledge selector")
    )


class DataSourceWebNode(INode):
    serializer_class = DataSourceWebNodeParamsSerializer
    supported_workflow_type_list = [WorkflowType.KNOWLEDGE]
    type = "data-source-web-node"

    @staticmethod
    def get_form_list(node):
        return [
            {
                "field": "source_url",
                "input_type": "TextInput",
                "attrs": {"placeholder": _("Please enter the Web root address")},
                "label": _("Web source url"),
                "required": True,
            },
            {
                "field": "selector",
                "input_type": "TextInput",
                "attrs": {"placeholder": _("The default is body, you can enter .classname/#idname/tagname")},
                "label": _("Web knowledge selector"),
                "required": False,
            },
        ]

    def _get_collect_handler(self, document_list):
        def handler(child_link: ChildLink, response: Fork.Response):
            if response.status != 200:
                raise ValueError(response.message or f"Failed to fetch Web source: {child_link.url}")
            document_name = (
                child_link.tag.text
                if child_link.tag is not None and len(child_link.tag.text.strip()) > 0
                else child_link.url
            )
            document_list.append({"name": document_name.strip(), "content": response.content})
            # 已取消则抛出 CancelledException,由引擎结束流程
            self._check_cancelled()

        return handler

    def execute(self):
        workflow_params = self.get_workflow_parameters()
        data_source = workflow_params.get("data_source") or {}

        serializer = self.serializer_class(data=data_source)
        serializer.is_valid(raise_exception=True)
        source_url = serializer.validated_data.get("source_url")
        selector = serializer.validated_data.get("selector") or "body"

        document_list = []
        collect_handler = self._get_collect_handler(document_list)

        try:
            ForkManage(source_url, selector.split(" ") if selector else []).fork(3, set(), collect_handler)
        except CancelledException:
            raise
        except Exception as e:
            maxkb_logger.error(
                _("data source web node:{node_id} error{error}{traceback}").format(
                    node_id=self.get_node_id(), error=str(e), traceback=traceback.format_exc()
                )
            )
            raise

        self.write_context("document_list", document_list)
        self.write_context("source_url", source_url)
        self.write_context("selector", selector)

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "document_list": self.get_context("document_list"),
                "source_url": self.get_context("source_url"),
                "selector": self.get_context("selector"),
                "knowledge_base": self.get_workflow_parameters().get("knowledge_base"),
                "enableException": self.node.properties.get("enableException"),
            }
        )
        return details
