# coding=utf-8
import asyncio
import json
from typing import List, Dict, Any

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from langchain_mcp_adapters.client import MultiServerMCPClient
from rest_framework import serializers

from application.workflow.common import WorkflowType
from application.workflow.i_node import INode
from application.workflow.status import Status
from common.utils.tool_code import ToolExecutor
from tools.models import Tool


class McpNodeSerializer(serializers.Serializer):
    mcp_servers = serializers.JSONField(required=True, label=_("Mcp servers"))
    mcp_server = serializers.CharField(required=True, label=_("Mcp server"))
    mcp_tool = serializers.CharField(required=True, label=_("Mcp tool"))
    mcp_tool_id = serializers.CharField(required=False, label=_("Mcp tool"), allow_null=True, allow_blank=True)
    mcp_source = serializers.CharField(required=False, label=_("Mcp source"), allow_blank=True, allow_null=True)
    tool_params = serializers.DictField(required=True, label=_("Tool parameters"))


class McpNode(INode):
    serializer_class = McpNodeSerializer
    supported_workflow_type_list = [WorkflowType.APPLICATION, WorkflowType.KNOWLEDGE, WorkflowType.TOOL]
    type = "mcp-node"

    def execute(self):
        node_params = self.get_parameters()

        mcp_servers = node_params.get("mcp_servers")
        mcp_server = node_params.get("mcp_server")
        mcp_tool = node_params.get("mcp_tool")
        mcp_tool_id = node_params.get("mcp_tool_id")
        mcp_source = node_params.get("mcp_source")
        tool_params = node_params.get("tool_params", {})

        if mcp_source == "referencing":
            if not mcp_tool_id:
                raise ValueError("MCP tool ID is required when mcp_source is 'referencing'.")
            tool = QuerySet(Tool).filter(id=mcp_tool_id).first()
            if not tool:
                raise ValueError(f"Tool with ID {mcp_tool_id} not found.")
            if not tool.is_active:
                raise ValueError(f"Tool with ID {mcp_tool_id} is inactive.")
            servers = json.loads(tool.code)
        else:
            servers = json.loads(mcp_servers) if isinstance(mcp_servers, str) else mcp_servers

        servers = self._handle_variables(servers)
        ToolExecutor().validate_mcp_transport(json.dumps(servers))

        params = json.loads(json.dumps(tool_params))
        params = self._handle_variables(params)

        self._check_cancelled()

        async def call_tool(t, a):
            client = MultiServerMCPClient(servers)
            async with client.session(mcp_server) as s:
                return await s.call_tool(t, a)

        res = asyncio.run(call_tool(mcp_tool, params))
        result = [content.text for content in res.content]

        self.write_context("result", result)
        self.write_context("tool_params", params)
        self.write_context("mcp_tool", mcp_tool)

    def _handle_variables(self, tool_params: Any) -> Any:
        if isinstance(tool_params, dict):
            for k, v in tool_params.items():
                tool_params[k] = self._handle_variables(v)
            return tool_params
        elif isinstance(tool_params, list):
            if len(tool_params) > 0 and isinstance(tool_params[0], str):
                return self._get_reference_content(tool_params)
            return [self._handle_variables(item) for item in tool_params]
        elif isinstance(tool_params, str):
            return self.workflow_manage.generate_prompt(tool_params)
        return tool_params

    def _get_reference_content(self, fields: List[str]) -> Any:
        if fields:
            return self.workflow_manage.get_reference_field(fields[0], fields[1:])
        return None

    def get_details(self, index: int = 0, position: dict = None, old_details: dict = None, **kwargs):
        details = super().get_details(index, position, old_details, **kwargs)
        details.update(
            {
                "mcp_tool": self.get_context("mcp_tool"),
                "tool_params": self.get_context("tool_params"),
                "result": self.get_context("result"),
            }
        )
        return details
