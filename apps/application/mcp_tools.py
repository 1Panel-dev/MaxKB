"""Shared MCP tool loading helpers."""

from common.mcp.client import create_mcp_client


async def get_mcp_tools(servers):
    client = create_mcp_client(servers)
    return await client.get_tools()
