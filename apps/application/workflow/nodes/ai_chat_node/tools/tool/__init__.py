# coding=utf-8
"""
@project: MaxKB
@Author:  虎虎虎
@file:    __init__.py
@date:    2026/9/15
@desc:
"""

from .custom import get_custom_tools
from .workflow import get_workflow_tools

__all__ = ["get_tool_tools", "get_workflow_tools", "get_custom_tools"]


def get_tool_tools(source_type, source_id, tool_ids, workspace_id, workflow_params=None):
    """
    构建工具（Tool）类工具：内部按 tool_type 拆分 workflow / custom，合并返回 LangChain tools。

    节点只需传入混合的 tool_ids，各构建器各自按 tool_type 过滤。
    """
    if not tool_ids:
        return []
    return get_workflow_tools(source_type, source_id, tool_ids, workspace_id, workflow_params) + get_custom_tools(
        source_type, source_id, tool_ids, workspace_id
    )
