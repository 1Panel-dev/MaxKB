# coding=utf-8

from typing import Type

from rest_framework import serializers

from application.flow.i_step_node import INode, NodeResult
from common.util.field_message import ErrMessage
from django.utils.translation import gettext_lazy as _


class McpNodeSerializer(serializers.Serializer):
    mcp_servers = serializers.JSONField(required=True,
                                        error_messages=ErrMessage.char(_("Mcp servers")))

    mcp_server = serializers.CharField(required=True,
                                       error_messages=ErrMessage.char(_("Mcp server")))

    mcp_tool = serializers.CharField(required=True, error_messages=ErrMessage.char(_("Mcp tool")))

    tool_params = serializers.DictField(required=True,
                                        error_messages=ErrMessage.char(_("Tool parameters")))


class IMcpNode(INode):
    type = 'mcp-node'

    def get_node_params_serializer_class(self) -> Type[serializers.Serializer]:
        return McpNodeSerializer

    def _run(self):
        return self.execute(**self.node_params_serializer.data, **self.flow_params_serializer.data)

    def execute(self, mcp_servers, mcp_server, mcp_tool, tool_params, **kwargs) -> NodeResult:
        pass
