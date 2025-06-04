# coding=utf-8

from typing import Type

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult


class McpNodeSerializer(serializers.Serializer):
    mcp_servers = serializers.JSONField(required=True,
                                        label=_("Mcp servers"))

    mcp_server = serializers.CharField(required=True,
                                       label=_("Mcp server"))

    mcp_tool = serializers.CharField(required=True, label=_("Mcp tool"))

    tool_params = serializers.DictField(required=True,
                                        label=_("Tool parameters"))


class IMcpNode(INode):
    type = 'mcp-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return McpNodeSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, mcp_servers, mcp_server, mcp_tool, tool_params, **kwargs) -> NodeResult:
        pass
