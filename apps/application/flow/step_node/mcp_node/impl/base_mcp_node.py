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
        tool_params = {'query': '中北大学如何'}

        async def call_tool(servers, tool_params):
            async with MultiServerMCPClient(servers) as client:
                print(tool_params)
                s = await client.sessions['composio_search'].call_tool(mcp_tool, tool_params)

                return s

        res = asyncio.run(call_tool(servers, tool_params))
        print(res)
        return NodeResult({'result': ''}, {})

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
