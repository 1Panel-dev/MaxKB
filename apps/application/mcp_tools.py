"""Shared MCP tool loading helpers."""

from langchain_mcp_adapters.client import MultiServerMCPClient


async def get_mcp_tools(servers):
    client = MultiServerMCPClient(servers)
    return await client.get_tools()
