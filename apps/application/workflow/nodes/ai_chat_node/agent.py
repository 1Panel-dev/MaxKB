# coding=utf-8
"""
@project: MaxKB
@Author:虎虎虎
@file:  agent.py
@date:  2026/9/14 16:59
@desc:  AI 对话节点的 Agent（MCP / deepagents）执行逻辑。

从 application/flow/tools.py 抽离，供新工作流引擎的 ai_chat_node 使用，
避免新引擎反向依赖旧引擎的 flow.tools 模块。
"""

import asyncio
import json
import os
import re
import shutil

import langchain_core.messages.ai as _lc_ai_module
import uuid_utils.compat as uuid
from deepagents import create_deep_agent
from langchain_core.utils._merge import merge_lists as _original_merge_lists
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import MemorySaver

from application.workflow.backend.sandbox_shell import SandboxShellBackend
from application.workflow.i_node import CancelledException
from application.workflow.nodes.ai_chat_node.tools.skill import init_skills
from maxkb.const import CONFIG


# ---------------------------------------------------------------------------
# Fix: qwen's OpenAI-compatible streaming sends id='' (empty string) for
# intermediate tool_call_chunks while only the first chunk carries the real
# id ('call_xxx...'). langchain-core's merge_lists treats '' != 'call_xxx' as
# an ID conflict and _appends_ instead of merging → the accumulated AIMessage
# ends up with two separate tool_calls (one with empty args, one with empty
# id) instead of one correct entry. This causes the Qwen API to reject the
# next request with "function.arguments must be in JSON format".
#
# Patch: normalise id='' → None for items that have an 'index' key
# (i.e. tool_call_chunk dicts). merge_lists treats None as "no id" and will
# merge with any existing entry, keeping the real id from the first chunk.
# ---------------------------------------------------------------------------
def _merge_lists_normalize_empty_tool_chunk_ids(left, *others):
    """Wrapper around merge_lists that normalises empty-string IDs to None in
    tool_call_chunk items (those with an 'index' key) so that qwen streaming
    chunks with id='' are merged correctly by index."""

    def _norm(lst):
        if lst is None:
            return lst
        result = []
        for item in lst:
            if isinstance(item, dict) and "index" in item and item.get("id") == "":
                item = {**item, "id": None}
            result.append(item)
        return result

    return _original_merge_lists(
        _norm(left),
        *[_norm(o) for o in others],
    )


# Replace the module-level reference used by add_ai_message_chunks in ai.py
_lc_ai_module.merge_lists = _merge_lists_normalize_empty_tool_chunk_ids


def _get_tool_call_id(raw_id):
    if not raw_id:
        return None
    if not isinstance(raw_id, str):
        raw_id = str(raw_id)

    s = raw_id
    prefix = "call_"
    positions = [m.start() for m in re.finditer(re.escape(prefix), s)]
    if not positions:
        return raw_id

    # 取最后一个前缀位置，截到下一个前缀或结尾
    start = positions[-1]
    end = len(s)
    for pos in positions:
        if pos > start:
            end = pos
            break

    tool_id = s[start:end]
    return tool_id or raw_id


class ToolCallStreamManagement:
    def __init__(self):
        self.index_id_map = {}
        self.id_name_map = {}
        self.tool_uuid_map = {}
        self.use_tool_id_list = set()

    @staticmethod
    def get_fallback_tool_calls(msg):
        source = msg.tool_calls or msg.invalid_tool_calls
        if source:
            return [(tc.get("index"), tc.get("id"), tc.get("name"), tc.get("args", "")) for tc in source]
        result = []
        for tc in msg.additional_kwargs.get("tool_calls", []):
            func = tc.get("function")
            if isinstance(func, dict):
                result.append((tc.get("index"), tc.get("id"), func.get("name"), func.get("arguments", "")))
            else:
                result.append((tc.get("index"), tc.get("id"), tc.get("name"), tc.get("arguments", "")))
        return result

    def get_tool_id(self, index, raw_id):
        if raw_id and str(raw_id).strip():
            tool_id = _get_tool_call_id(str(raw_id).strip())
            if index is not None:
                self.index_id_map[index] = tool_id
            return tool_id
        if index is not None:
            return self.index_id_map.get(index)
        return None

    def get_tool_name(self, tool_id, default=None):
        return self.id_name_map.get(tool_id, default)

    def add_tool_id(self, tool_id):
        self.use_tool_id_list.add(tool_id)

    def get_tool_uuid(self, tool_id):
        if tool_id not in self.tool_uuid_map:
            self.tool_uuid_map[tool_id] = str(uuid.uuid7())
        return self.tool_uuid_map.get(tool_id)

    def tool_id_is_used(self, tool_id):
        return tool_id in self.use_tool_id_list

    def set_tool_id_name(self, tool_id, name):
        self.id_name_map[tool_id] = name


def create_agent(
    chat_model,
    system_prompt,
    message_list,
    mcp_servers,
    call_back,
    chat_id=None,
    skill_tool_ids=None,
    extra_tools=None,
):
    # 创建临时文件夹
    if chat_id:
        temp_dir = os.path.join("/tmp", chat_id)
    else:
        temp_dir = os.path.join("/tmp", str(uuid.uuid7()))
    skills_dir = os.path.join(temp_dir, "skills")
    os.makedirs(skills_dir, exist_ok=True)

    async def _run():
        checkpointer = MemorySaver()
        await init_skills(skill_tool_ids, temp_dir)
        client = MultiServerMCPClient(json.loads(mcp_servers))
        tools = await client.get_tools()
        for tool in tools:
            tool.handle_tool_error = True
        if extra_tools:
            for tool in extra_tools:
                tools.append(tool)

        agent = create_deep_agent(
            model=chat_model,
            backend=SandboxShellBackend(root_dir=temp_dir, virtual_mode=True),
            skills=["/skills"],
            tools=tools,
            system_prompt=system_prompt,
            interrupt_on={"write_file": False, "read_file": False, "edit_file": False},
            checkpointer=checkpointer,
        )
        recursion_limit = int(CONFIG.get("LANGCHAIN_GRAPH_RECURSION_LIMIT", "100"))
        response = agent.astream(
            {"messages": message_list},
            config={"recursion_limit": recursion_limit, "configurable": {"thread_id": chat_id}},
            stream_mode="messages",
        )

        async for chunk in response:
            msg = chunk[0]
            call_back.on_next(msg)

    def _classify_error(e):
        # 取消：原样保留（保持节点取消语义）；MCP TaskGroup 的 ExceptionGroup：展开取真实异常并包成 RuntimeError
        if isinstance(e, CancelledException):
            return e
        if isinstance(e, ExceptionGroup):
            while isinstance(e, ExceptionGroup):
                e = e.exceptions[0]
        return RuntimeError(f"{type(e).__name__}: {str(e)}")

    error = None
    try:
        asyncio.run(_run())
    except Exception as e:
        error = _classify_error(e)
    finally:
        # 清理临时文件夹
        shutil.rmtree(temp_dir, ignore_errors=True)
    call_back.on_complete(error)
