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

from tools.models import Tool, ToolType
from common.utils.workflow_reference import require_workflow_tools


def get_referenced_mcp_tools(ids, workflow_params):
    require_workflow_tools(ids, workflow_params.get("workflow_user_id"), workflow_params.get("workspace_id"))
    return QuerySet(Tool).filter(id__in=ids, tool_type=ToolType.MCP, is_active=True)


def get_mcp_servers(mcp_source, mcp_servers, mcp_tool_id, mcp_tool_ids, handle_variables, workflow_params):
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
        mcp_tools = get_referenced_mcp_tools(mcp_tool_ids, workflow_params).values()
        for mcp_tool in mcp_tools:
            if mcp_tool and mcp_tool["is_active"]:
                mcp_servers_config = handle_variables({**mcp_servers_config, **json.loads(mcp_tool["code"])})
    return mcp_servers_config
