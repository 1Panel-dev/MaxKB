# coding=utf-8
import asyncio
import json
from typing import List

from django.db.models import QuerySet
from langchain_mcp_adapters.client import MultiServerMCPClient

from application.flow.i_step_node import NodeResult
from application.flow.step_node.mcp_node.i_mcp_node import IMcpNode
from tools.models import Tool


class BaseMcpNode(IMcpNode):
    def save_context(self, details, workflow_manage):
        self.context['result'] = details.get('result')
        self.context['tool_params'] = details.get('tool_params')
        self.context['mcp_tool'] = details.get('mcp_tool')
        self.context['exception_message'] = details.get('err_message')

    def execute(self, mcp_servers, mcp_server, mcp_tool, mcp_tool_id, mcp_source, tool_params, **kwargs) -> NodeResult:
        if mcp_source == 'referencing':
            if not mcp_tool_id:
                raise ValueError("MCP tool ID is required when mcp_source is 'referencing'.")
            tool = QuerySet(Tool).filter(id=mcp_tool_id).first()
            if not tool:
                raise ValueError(f"Tool with ID {mcp_tool_id} not found.")
            if not tool.is_active:
                raise ValueError(f"Tool with ID {mcp_tool_id} is inactive.")
            servers = json.loads(tool.code)
            servers = self.handle_variables(servers)  # 处理servers中的变量
            params = json.loads(json.dumps(tool_params))
            params = self.handle_variables(params)
        else:
            servers = json.loads(mcp_servers)
            servers = self.handle_variables(servers)  # 处理servers中的变量
            params = json.loads(json.dumps(tool_params))
            params = self.handle_variables(params)

        async def call_tool(t, a):
            client = MultiServerMCPClient(servers)
            async with client.session(mcp_server) as s:
                return await s.call_tool(t, a)

        res = asyncio.run(call_tool(mcp_tool, params))
        return NodeResult(
            {'result': [content.text for content in res.content], 'tool_params': params, 'mcp_tool': mcp_tool}, {})

    def handle_variables(self, tool_params):
        # 处理参数中的变量
        for k, v in tool_params.items():
            if type(v) == str:
                tool_params[k] = self.workflow_manage.generate_prompt(tool_params[k])
            if type(v) == dict:
                self.handle_variables(v)
            if (type(v) == list) and (type(v[0]) == str):
                tool_params[k] = self.get_reference_content(v)
        return tool_params

    def get_reference_content(self, fields: List[str]):
        return self.workflow_manage.get_reference_field(
            fields[0],
            fields[1:])

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'status': self.status,
            'err_message': self.err_message,
            'type': self.node.type,
            'mcp_tool': self.context.get('mcp_tool'),
            'tool_params': self.context.get('tool_params'),
            'result': self.context.get('result'),
            'enableException': self.node.properties.get('enableException'),
        }
