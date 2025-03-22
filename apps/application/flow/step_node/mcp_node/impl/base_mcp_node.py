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
        self.context['question'] = details.get('question')
        self.answer_text = details.get('result')

    def execute(self, mcp_servers, mcp_server, mcp_tool, tool_params, **kwargs) -> NodeResult:
        servers = json.loads(mcp_servers)
        arguments = {
            'params': tool_params
        }

        async def call_tool(s, session, t, a):
            async with MultiServerMCPClient(s) as client:
                s = await client.sessions[session].call_tool(t, a)
                return s

        res = asyncio.run(call_tool(servers, mcp_server, mcp_tool, arguments))
        return NodeResult({'result': [content.text for content in res.content]}, {})

    def get_reference_content(self, fields: List[str]):
        return str(self.workflow_manage.get_reference_field(
            fields[0],
            fields[1:]))

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'question': self.context.get('question'),
            'result': self.context.get('result'),
        }
