# coding=utf-8
"""
@project: MaxKB
@Author:  虎虎虎
@file:    mcp.py
@date:    2026/9/15
@desc:
"""

import json

from django.db.models import QuerySet

from tools.models import Tool


def get_mcp_servers(mcp_source, mcp_servers, mcp_tool_id, mcp_tool_ids, handle_variables):
    """
    tool-mcp-custom：mcp_source == "custom" 时用节点传入的自定义 MCP JSON。
    tool-mcp：否则用库内 MCP 工具（Tool.code 存 MCP server 配置）。
    """
    if mcp_source is None:
        mcp_source = "custom"
    if not mcp_tool_ids:
        mcp_tool_ids = []
    if mcp_tool_id:
        mcp_tool_ids = list(set(mcp_tool_ids + [mcp_tool_id]))

    mcp_servers_config = {}
    if mcp_source == "custom" and mcp_servers:
        mcp_servers_config = handle_variables(json.loads(mcp_servers))
    elif mcp_tool_ids:
        mcp_tools = QuerySet(Tool).filter(id__in=mcp_tool_ids).values()
        for mcp_tool in mcp_tools:
            if mcp_tool and mcp_tool["is_active"]:
                mcp_servers_config = handle_variables({**mcp_servers_config, **json.loads(mcp_tool["code"])})
    return mcp_servers_config
