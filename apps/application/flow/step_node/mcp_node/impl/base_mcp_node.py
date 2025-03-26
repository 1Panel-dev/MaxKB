# coding=utf-8
import asyncio
import json
from typing import List

from langchain_mcp_adapters.client import MultiServerMCPClient

from application.flow.i_step_node import NodeResult
from application.flow.step_node.mcp_node.i_mcp_node import IMcpNode


class BaseMcpNode(IMcpNode):
    def save_context(self, details, workflow_manage):
        self.context['result'] = details.get('result')
        self.context['tool_params'] = details.get('tool_params')
        self.context['mcp_tool'] = details.get('mcp_tool')
        self.answer_text = details.get('result')

    def execute(self, mcp_servers, mcp_server, mcp_tool, tool_params, **kwargs) -> NodeResult:
        servers = json.loads(mcp_servers)
        params = json.loads(json.dumps(tool_params))
        params = self.handle_variables(params)

        async def call_tool(s, session, t, a):
            async with MultiServerMCPClient(s) as client:
                s = await client.sessions[session].call_tool(t, a)
                return s

        res = asyncio.run(call_tool(servers, mcp_server, mcp_tool, params))
        return NodeResult({'result': [content.text for content in res.content], 'tool_params': params, 'mcp_tool': mcp_tool}, {})

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
        return str(self.workflow_manage.get_reference_field(
            fields[0],
            fields[1:]))

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
        }
