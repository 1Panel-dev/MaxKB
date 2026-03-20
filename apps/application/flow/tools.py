# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： utils.py
    @date：2024/6/6 15:15
    @desc:
"""
from tools.models import ToolRecord, Tool
from maxkb.const import CONFIG
from knowledge.models.knowledge_action import State
from knowledge.models import File
from common.utils.logger import maxkb_logger
from common.result import result
from application.flow.i_step_node import WorkFlowPostHandler
from application.flow.backend.sandbox_shell import SandboxShellBackend
import asyncio
import io
import json
import os
import queue
import re
import shutil
import threading
import zipfile
from functools import reduce
from typing import Iterator

import uuid_utils.compat as uuid
from asgiref.sync import sync_to_async
from deepagents import create_deep_agent
from django.db.models import QuerySet
from django.http import StreamingHttpResponse
from langchain_core.messages import BaseMessageChunk, BaseMessage, ToolMessage, AIMessageChunk
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import MemorySaver

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
import langchain_core.messages.ai as _lc_ai_module
from langchain_core.utils._merge import merge_lists as _original_merge_lists


def _merge_lists_normalize_empty_tool_chunk_ids(left, *others):
    """Wrapper around merge_lists that normalises empty-string IDs to None in
    tool_call_chunk items (those with an 'index' key) so that qwen streaming
    chunks with id='' are merged correctly by index."""
    def _norm(lst):
        if lst is None:
            return lst
        result = []
        for item in lst:
            if isinstance(item, dict) and 'index' in item and item.get('id') == '':
                item = {**item, 'id': None}
            result.append(item)
        return result

    return _original_merge_lists(
        _norm(left),
        *[_norm(o) for o in others],
    )


# Replace the module-level reference used by add_ai_message_chunks in ai.py
_lc_ai_module.merge_lists = _merge_lists_normalize_empty_tool_chunk_ids


class Reasoning:
    def __init__(self, reasoning_content_start, reasoning_content_end):
        self.content = ""
        self.reasoning_content = ""
        self.all_content = ""
        self.reasoning_content_start_tag = reasoning_content_start
        self.reasoning_content_end_tag = reasoning_content_end
        self.reasoning_content_start_tag_len = len(
            reasoning_content_start) if reasoning_content_start is not None else 0
        self.reasoning_content_end_tag_len = len(
            reasoning_content_end) if reasoning_content_end is not None else 0
        self.reasoning_content_end_tag_prefix = reasoning_content_end[
            0] if self.reasoning_content_end_tag_len > 0 else ''
        self.reasoning_content_is_start = False
        self.reasoning_content_is_end = False
        self.reasoning_content_chunk = ""

    def get_end_reasoning_content(self):
        if not self.reasoning_content_is_start and not self.reasoning_content_is_end:
            r = {'content': self.all_content, 'reasoning_content': ''}
            self.reasoning_content_chunk = ""
            return r
        if self.reasoning_content_is_start and not self.reasoning_content_is_end:
            r = {'content': '', 'reasoning_content': self.reasoning_content_chunk}
            self.reasoning_content_chunk = ""
            return r
        return {'content': '', 'reasoning_content': ''}

    def _normalize_content(self, content):
        """将不同类型的内容统一转换为字符串"""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # 处理包含多种内容类型的列表
            normalized_parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get('type') == 'text':
                        normalized_parts.append(item.get('text', ''))
            return ''.join(normalized_parts)
        else:
            return str(content)

    def get_reasoning_content(self, chunk):
        # 如果没有开始思考过程标签那么就全是结果
        if self.reasoning_content_start_tag is None or len(self.reasoning_content_start_tag) == 0:
            self.content += chunk.content
            return {'content': chunk.content, 'reasoning_content': ''}
        # 如果没有结束思考过程标签那么就全部是思考过程
        if self.reasoning_content_end_tag is None or len(self.reasoning_content_end_tag) == 0:
            return {'content': '', 'reasoning_content': chunk.content}
        chunk.content = self._normalize_content(chunk.content)
        self.all_content += chunk.content
        if not self.reasoning_content_is_start and len(self.all_content) >= self.reasoning_content_start_tag_len:
            if self.all_content.startswith(self.reasoning_content_start_tag):
                self.reasoning_content_is_start = True
                self.reasoning_content_chunk = self.all_content[self.reasoning_content_start_tag_len:]
            else:
                if not self.reasoning_content_is_end:
                    self.reasoning_content_is_end = True
                    self.content += self.all_content
                    return {'content': self.all_content,
                            'reasoning_content': chunk.additional_kwargs.get('reasoning_content',
                                                                             '') if chunk.additional_kwargs else ''
                            }
        else:
            if self.reasoning_content_is_start:
                self.reasoning_content_chunk += chunk.content
        reasoning_content_end_tag_prefix_index = self.reasoning_content_chunk.find(
            self.reasoning_content_end_tag_prefix)
        if self.reasoning_content_is_end:
            self.content += chunk.content
            return {'content': chunk.content, 'reasoning_content': chunk.additional_kwargs.get('reasoning_content',
                                                                                               '') if chunk.additional_kwargs else ''
                    }
        # 是否包含结束
        if reasoning_content_end_tag_prefix_index > -1:
            if len(self.reasoning_content_chunk) - reasoning_content_end_tag_prefix_index >= self.reasoning_content_end_tag_len:
                reasoning_content_end_tag_index = self.reasoning_content_chunk.find(
                    self.reasoning_content_end_tag)
                if reasoning_content_end_tag_index > -1:
                    reasoning_content_chunk = self.reasoning_content_chunk[
                        0:reasoning_content_end_tag_index]
                    content_chunk = self.reasoning_content_chunk[
                        reasoning_content_end_tag_index + self.reasoning_content_end_tag_len:]
                    self.reasoning_content += reasoning_content_chunk
                    self.content += content_chunk
                    self.reasoning_content_chunk = ""
                    self.reasoning_content_is_end = True
                    return {'content': content_chunk, 'reasoning_content': reasoning_content_chunk}
                else:
                    reasoning_content_chunk = self.reasoning_content_chunk[
                        0:reasoning_content_end_tag_prefix_index + 1]
                    self.reasoning_content_chunk = self.reasoning_content_chunk.replace(
                        reasoning_content_chunk, '')
                    self.reasoning_content += reasoning_content_chunk
                    return {'content': '', 'reasoning_content': reasoning_content_chunk}
            else:
                return {'content': '', 'reasoning_content': ''}

        else:
            if self.reasoning_content_is_end:
                self.content += chunk.content
                return {'content': chunk.content, 'reasoning_content': chunk.additional_kwargs.get('reasoning_content',
                                                                                                   '') if chunk.additional_kwargs else ''
                        }
            else:
                # aaa
                result = {'content': '',
                          'reasoning_content': self.reasoning_content_chunk}
                self.reasoning_content += self.reasoning_content_chunk
                self.reasoning_content_chunk = ""
                return result


def event_content(chat_id, chat_record_id, response, workflow,
                  write_context,
                  post_handler: WorkFlowPostHandler):
    """
    用于处理流式输出
    @param chat_id:         会话id
    @param chat_record_id:  对话记录id
    @param response:        响应数据
    @param workflow:        工作流管理器
    @param write_context    写入节点上下文
    @param post_handler:    后置处理器
    """
    answer = ''
    try:
        for chunk in response:
            answer += chunk.content
            yield 'data: ' + json.dumps({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                                         'content': chunk.content, 'is_end': False}, ensure_ascii=False) + "\n\n"
        write_context(answer, 200)
        post_handler.handler(chat_id, chat_record_id, answer, workflow)
        yield 'data: ' + json.dumps({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                                     'content': '', 'is_end': True}, ensure_ascii=False) + "\n\n"
    except Exception as e:
        answer = str(e)
        write_context(answer, 500)
        post_handler.handler(chat_id, chat_record_id, answer, workflow)
        yield 'data: ' + json.dumps({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                                     'content': answer, 'is_end': True}, ensure_ascii=False) + "\n\n"


def to_stream_response(chat_id, chat_record_id, response: Iterator[BaseMessageChunk], workflow, write_context,
                       post_handler):
    """
    将结果转换为服务流输出
    @param chat_id:        会话id
    @param chat_record_id: 对话记录id
    @param response:       响应数据
    @param workflow:       工作流管理器
    @param write_context   写入节点上下文
    @param post_handler:   后置处理器
    @return: 响应
    """
    r = StreamingHttpResponse(
        streaming_content=event_content(
            chat_id, chat_record_id, response, workflow, write_context, post_handler),
        content_type='text/event-stream;charset=utf-8',
        charset='utf-8')

    r['Cache-Control'] = 'no-cache'
    return r


def to_response(chat_id, chat_record_id, response: BaseMessage, workflow, write_context,
                post_handler: WorkFlowPostHandler):
    """
    将结果转换为服务输出

    @param chat_id:        会话id
    @param chat_record_id: 对话记录id
    @param response:       响应数据
    @param workflow:       工作流管理器
    @param write_context   写入节点上下文
    @param post_handler:   后置处理器
    @return: 响应
    """
    answer = response.content
    write_context(answer)
    post_handler.handler(chat_id, chat_record_id, answer, workflow)
    return result.success({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                           'content': answer, 'is_end': True})


def to_response_simple(chat_id, chat_record_id, response: BaseMessage, workflow,
                       post_handler: WorkFlowPostHandler):
    answer = response.content
    post_handler.handler(chat_id, chat_record_id, answer, workflow)
    return result.success({'chat_id': str(chat_id), 'id': str(chat_record_id), 'operate': True,
                           'content': answer, 'is_end': True})


def to_stream_response_simple(stream_event):
    r = StreamingHttpResponse(
        streaming_content=stream_event,
        content_type='text/event-stream;charset=utf-8',
        charset='utf-8')

    r['Cache-Control'] = 'no-cache'
    return r


def generate_tool_message_complete(icon, name, input_content, output_content):
    """生成包含输入和输出的工具消息模版"""
    # 确保输入内容是字符串，如果不是则尝试转换为 JSON 字符串
    if not isinstance(input_content, str):
        input_content = json.dumps(input_content, ensure_ascii=False)
    # 格式化输出
    if not isinstance(output_content, str):
        output_content = json.dumps(output_content, ensure_ascii=False)
    content = {
        "icon": icon,
        "title": name,
        "type": "simple-tool-calls",
        "content": {
            "input": input_content,
            "output": output_content
        }
    }
    return f'<tool_calls_render>{json.dumps(content)}</tool_calls_render>'


# 全局单例事件循环
_global_loop = None
_loop_thread = None
_loop_lock = threading.Lock()


def get_global_loop():
    """获取全局共享的事件循环"""
    global _global_loop, _loop_thread

    with _loop_lock:
        if _global_loop is None:
            _global_loop = asyncio.new_event_loop()

            def run_forever():
                asyncio.set_event_loop(_global_loop)
                _global_loop.run_forever()

            _loop_thread = threading.Thread(
                target=run_forever, daemon=True, name="GlobalAsyncLoop")
            _loop_thread.start()

    return _global_loop


def _extract_tool_id(raw_id):
    """从 raw_id 中提取最后一个符合 call_... 模式的 id，若无匹配则返回原值或 None"""
    if not raw_id:
        return None
    if not isinstance(raw_id, str):
        raw_id = str(raw_id)

    s = raw_id
    prefix = 'call_'
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


async def _initialize_skills(mcp_servers, temp_dir):
    skills_dir = os.path.join(temp_dir, 'skills')
    mcp_config = json.loads(mcp_servers)
    if "skills" in mcp_config:
        skill_file_items = mcp_config.pop('skills')
        for skill_file in skill_file_items:
            # 使用 sync_to_async 包装 ORM 查询
            file = await sync_to_async(lambda: QuerySet(File).filter(id=skill_file['file_id']).first())()
            if not file:
                continue
            # get_bytes 可能也涉及 IO，也用 sync_to_async 包装
            file_bytes = await sync_to_async(file.get_bytes)()
            params = skill_file.get('params', {})
            with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as zip_ref:
                members = [
                    m for m in zip_ref.namelist()
                    if not m.startswith('__MACOSX/') and '__MACOSX' not in m
                ]
                for member in members:
                    if ".." in member or member.startswith("/"):
                        raise ValueError(f"非法路径: {member}")
                zip_ref.extractall(skills_dir, members=members)

                # 获取技能解压后的顶级目录名
                top_level_dirs = set()
                for member in members:
                    parts = member.split('/')
                    if parts[0]:
                        top_level_dirs.add(parts[0])

                # 将 params 写入每个顶级目录下的 .env 文件
                if params:
                    env_lines = []
                    for key, value in params.items():
                        # 对含空格或特殊字符的值加引号
                        env_lines.append(f'{key}={value}')
                    env_content = '\n'.join(env_lines) + '\n'
                    for top_dir in top_level_dirs:
                        env_path = os.path.join(skills_dir, top_dir, '.env')
                        with open(env_path, 'w', encoding='utf-8') as f:
                            f.write(env_content)

        os.system("chmod -R g+rx " + temp_dir)  # 确保技能目录可访问

    client = MultiServerMCPClient(mcp_config)

    return client


async def _yield_mcp_response(chat_model, message_list, mcp_servers, mcp_output_enable=True, tool_init_params={},
                              source_id=None, source_type=None, temp_dir=None, chat_id=None):
    try:
        checkpointer = MemorySaver()
        client = await _initialize_skills(mcp_servers, temp_dir)
        tools = await client.get_tools()
        agent = create_deep_agent(
            model=chat_model,
            backend=SandboxShellBackend(root_dir=temp_dir, virtual_mode=True),
            skills=['/skills'],
            tools=tools,
            interrupt_on={
                "write_file": False,
                "read_file": False,
                "edit_file": False
            },
            checkpointer=checkpointer,
        )
        recursion_limit = int(CONFIG.get(
            "LANGCHAIN_GRAPH_RECURSION_LIMIT", '100'))
        response = agent.astream(
            {"messages": message_list},
            config={"recursion_limit": recursion_limit,
                    "configurable": {"thread_id": chat_id}},
            stream_mode='messages'
        )

        tool_calls_info = {}  # tool_id -> {'name': ..., 'input': ...}
        # key(index/id) -> {'id': ..., 'name': ..., 'arguments': ...}
        _tool_fragments = {}

        def _merge_arguments(entry, part_args):
            if not isinstance(part_args, str):
                try:
                    part_args = json.dumps(part_args, ensure_ascii=False)
                except Exception:
                    part_args = str(part_args) if part_args else ''
            if not part_args:
                return

            # Some providers first emit placeholder args like "{}" and then
            # stream the real JSON fragments via later chunks. Prefer fragments.
            if entry['arguments'] in ('{}', '[]') and part_args.startswith('{'):
                entry['arguments'] = part_args
                return

            if entry['arguments']:
                try:
                    existing_obj = json.loads(entry['arguments'])
                    new_obj = json.loads(part_args)
                    if isinstance(existing_obj, dict) and isinstance(new_obj, dict):
                        merged = {**existing_obj, **new_obj}
                        entry['arguments'] = json.dumps(
                            merged, ensure_ascii=False)
                    else:
                        entry['arguments'] += part_args
                except (json.JSONDecodeError, ValueError):
                    entry['arguments'] += part_args
            else:
                entry['arguments'] = part_args

        def _get_fragment_key(idx, raw_id):
            if idx is not None:
                return f'idx:{idx}'
            if raw_id and str(raw_id).strip():
                return f"id:{_extract_tool_id(str(raw_id).strip())}"
            return None

        def _upsert_fragment(key, raw_id, func_name, part_args):
            if key is None:
                return
            entry = _tool_fragments.setdefault(
                key, {'id': '', 'name': '', 'arguments': ''})

            if raw_id and str(raw_id).strip():
                new_id = str(raw_id).strip()
                if entry.get('completed') and entry.get('id') and entry['id'] != new_id:
                    maxkb_logger.debug(
                        f"Resetting completed fragment {key}: old ID {entry['id']} -> new ID {new_id}")
                    entry.clear()
                    entry.update({'id': '', 'name': '', 'arguments': ''})
                entry['id'] = new_id

            if func_name:
                entry['name'] = func_name

            _merge_arguments(entry, part_args)

        async for chunk in response:
            # print(chunk)
            if isinstance(chunk[0], AIMessageChunk):
                # ----------------------------------------------------------------
                # 1. 从 tool_call_chunks 中聚合工具调用片段
                #    (qwen/OpenAI streaming 通过 tool_call_chunks 传递，
                #     additional_kwargs['tool_calls'] 在流式时通常为空)
                # ----------------------------------------------------------------
                for tc_chunk in (chunk[0].tool_call_chunks or []):
                    raw_id = tc_chunk.get('id')
                    key = _get_fragment_key(tc_chunk.get('index'), raw_id)
                    _upsert_fragment(
                        key,
                        raw_id,
                        tc_chunk.get('name'),
                        tc_chunk.get('args', '')
                    )

                # ----------------------------------------------------------------
                # 1.1 兼容部分模型将工具调用放在 chunk.tool_calls，且 tool_call_chunks
                #     的 index 为空（例如 ollama/qwen）
                # ----------------------------------------------------------------
                has_tool_call_chunks = bool(chunk[0].tool_call_chunks)
                for tool_call in (chunk[0].tool_calls or []):
                    raw_id = tool_call.get('id')
                    part_args = tool_call.get('args', '')
                    # qwen-plus often emits {} here as a placeholder while
                    # the real args are split in tool_call_chunks/invalid_tool_calls.
                    if has_tool_call_chunks and (
                        part_args == '' or part_args == {} or part_args == []
                    ):
                        part_args = ''
                    key = _get_fragment_key(tool_call.get('index'), raw_id)
                    _upsert_fragment(
                        key,
                        raw_id,
                        tool_call.get('name'),
                        part_args
                    )

                # ----------------------------------------------------------------
                # 1.2 兼容 invalid_tool_calls 分片（部分模型会把中间 JSON 片段放这里）
                # ----------------------------------------------------------------
                for invalid_tool_call in (chunk[0].invalid_tool_calls or []):
                    raw_id = invalid_tool_call.get('id')
                    key = _get_fragment_key(
                        invalid_tool_call.get('index'), raw_id)
                    _upsert_fragment(
                        key,
                        raw_id,
                        invalid_tool_call.get('name'),
                        invalid_tool_call.get('args', '')
                    )

                # ----------------------------------------------------------------
                # 2. 兼容 additional_kwargs['tool_calls'] 方式（旧格式/非流式情况）
                # ----------------------------------------------------------------
                legacy_tool_calls = chunk[0].additional_kwargs.get(
                    'tool_calls', [])
                for tool_call in legacy_tool_calls:
                    raw_id = tool_call.get('id')
                    func = tool_call.get('function', {})
                    if isinstance(func, dict):
                        func_name = func.get('name')
                        part_args = func.get('arguments', '')
                    else:
                        func_name = tool_call.get('name')
                        part_args = tool_call.get('arguments', '')
                    key = _get_fragment_key(tool_call.get('index'), raw_id)
                    _upsert_fragment(key, raw_id, func_name, part_args)

                # ----------------------------------------------------------------
                # 3. 检测工具调用结束，更新 tool_calls_info
                # ----------------------------------------------------------------
                is_finish_chunk = (
                    chunk[0].response_metadata.get(
                        'finish_reason') == 'tool_calls'
                    or chunk[0].chunk_position == 'last'
                )

                if is_finish_chunk:
                    # 在 finish chunk 时，将所有未完成的 fragment 标记完成并更新 tool_calls_info
                    maxkb_logger.debug(
                        f"Processing finish chunk. Tool fragments: {_tool_fragments}")
                    for idx, entry in _tool_fragments.items():
                        if entry.get('completed'):
                            maxkb_logger.debug(
                                f"Skipping fragment {idx}: already completed")
                            continue
                        if not entry.get('id'):
                            maxkb_logger.debug(
                                f"Skipping fragment {idx}: missing id. Fragment: {entry}")
                            continue
                        if not entry.get('arguments'):
                            maxkb_logger.debug(
                                f"Skipping fragment {idx}: missing arguments. Fragment: {entry}")
                            continue

                        if not entry.get('completed') and entry.get('id') and entry.get('arguments'):
                            try:
                                parsed_args = json.loads(entry['arguments'])
                                filtered_args = {
                                    k: v for k, v in parsed_args.items()
                                    if k not in tool_init_params
                                } if tool_init_params else parsed_args
                                normalized_id = _extract_tool_id(entry['id'])
                                info = {
                                    'name': entry['name'],
                                    'input': json.dumps(filtered_args, ensure_ascii=False)
                                }
                                tool_calls_info[entry['id']] = info
                                if normalized_id and normalized_id != entry['id']:
                                    tool_calls_info[normalized_id] = info
                                entry['completed'] = True
                                maxkb_logger.debug(
                                    f"Added tool call {entry['id']} to tool_calls_info")
                            except (json.JSONDecodeError, ValueError) as e:
                                # JSON parsing failed, but still add to tool_calls_info with raw arguments
                                # to prevent "Tool ID not found" errors when ToolMessage arrives
                                maxkb_logger.warning(
                                    f"Failed to parse tool arguments at finish for tool {entry.get('id', 'unknown')}: "
                                    f"{entry['arguments']}, error: {e}. Using raw arguments.")
                                normalized_id = _extract_tool_id(entry['id'])
                                info = {
                                    'name': entry['name'],
                                    # Use raw arguments
                                    'input': entry['arguments']
                                }
                                tool_calls_info[entry['id']] = info
                                if normalized_id and normalized_id != entry['id']:
                                    tool_calls_info[normalized_id] = info
                                entry['completed'] = True

                # ----------------------------------------------------------------
                # 4. 修复 tool_call_chunks 中的空 id（回填已知 id）
                # ----------------------------------------------------------------
                if chunk[0].tool_call_chunks:
                    for tc_chunk in chunk[0].tool_call_chunks:
                        key = _get_fragment_key(
                            tc_chunk.get('index'), tc_chunk.get('id'))
                        if key is not None:
                            frag = _tool_fragments.get(key)
                            if frag and frag.get('id') and not tc_chunk.get('id'):
                                tc_chunk['id'] = frag['id']

                # ----------------------------------------------------------------
                # 5. 修复 additional_kwargs['tool_calls']（兼容旧格式）
                #    仅在 finish chunk 时写入完整参数，避免污染中间 chunk 的
                #    additional_kwargs（中间 chunk 会被 ainvoke 累积，如果写入
                #    不完整 JSON 会导致下一轮 API 调用出现 arguments 非 JSON 格式错误）
                # ----------------------------------------------------------------
                if legacy_tool_calls and is_finish_chunk:
                    fixed_tool_calls = []
                    for tool_call in legacy_tool_calls:
                        key = _get_fragment_key(
                            tool_call.get('index'), tool_call.get('id'))
                        frag = _tool_fragments.get(
                            key) if key is not None else None
                        tc = dict(tool_call)
                        if frag and frag.get('id') and not tc.get('id'):
                            tc['id'] = frag['id']
                        if frag and isinstance(tc.get('function'), dict):
                            tc['function'] = dict(tc['function'])
                            if frag.get('completed'):
                                tc['function']['arguments'] = frag['arguments']
                        fixed_tool_calls.append(tc)
                    chunk[0].additional_kwargs['tool_calls'] = fixed_tool_calls

                yield chunk[0]

            if mcp_output_enable and isinstance(chunk[0], ToolMessage):
                tool_id = chunk[0].tool_call_id
                normalized_tool_id = _extract_tool_id(tool_id)
                tool_info = tool_calls_info.get(tool_id) or tool_calls_info.get(
                    normalized_tool_id)

                if tool_info:
                    try:
                        if isinstance(chunk[0].content, str):
                            tool_result = json.loads(chunk[0].content)
                        elif isinstance(chunk[0].content, dict):
                            tool_result = chunk[0].content
                        elif isinstance(chunk[0].content, list):
                            tool_result = chunk[0].content[0] if len(
                                chunk[0].content) > 0 else {}
                        else:
                            tool_result = {}
                        text = tool_result.get('text') if 'text' in tool_result else None
                        text_result = json.loads(text) if text else tool_result
                        if text:
                            tool_lib_id = text_result.pop('tool_id') if 'tool_id' in text_result else None
                        else:
                            tool_lib_id = tool_result.pop('tool_id') if 'tool_id' in tool_result else None
                        if tool_lib_id:
                            await save_tool_record(tool_lib_id, tool_info, tool_result, source_id, source_type)
                        tool_result = json.dumps(text_result, ensure_ascii=False)
                    except Exception as e:
                        tool_result = chunk[0].content
                    content = generate_tool_message_complete(
                        tool_info.get('icon', ''),
                        tool_info['name'],
                        tool_info['input'],
                        tool_result
                    )
                    chunk[0].content = content
                else:
                    maxkb_logger.warning(
                        f"Tool ID {tool_id} not found in tool_calls_info. "
                        f"Normalized Tool ID: {normalized_tool_id}. "
                        f"Available IDs: {list(tool_calls_info.keys())}. "
                        f"Tool fragments at this point: {_tool_fragments}"
                    )

                yield chunk[0]

    except ExceptionGroup as eg:
        def get_real_error(exc):
            if isinstance(exc, ExceptionGroup):
                return get_real_error(exc.exceptions[0])
            return exc

        real_error = get_real_error(eg)
        error_msg = f"{type(real_error).__name__}: {str(real_error)}"
        raise RuntimeError(error_msg) from None

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        raise RuntimeError(error_msg) from None


async def save_tool_record(tool_id, tool_info, tool_result, source_id, source_type):
    tool = await sync_to_async(lambda: QuerySet(Tool).filter(id=tool_id).first())()
    tool_info['icon'] = tool.icon
    tool_record = ToolRecord(
        id=uuid.uuid7(),
        workspace_id=tool.workspace_id,
        tool_id=tool_id,
        source_type=source_type,
        source_id=source_id,
        meta={'input': tool_info['input'], 'output': tool_result},
        state=State.SUCCESS
    )
    await sync_to_async(tool_record.save)()


def mcp_response_generator(chat_model, message_list, mcp_servers, mcp_output_enable=True, tool_init_params={},
                           source_id=None, source_type=None, chat_id=None):
    """使用全局事件循环，不创建新实例"""
    result_queue = queue.Queue()
    loop = get_global_loop()  # 使用共享循环
    # 创建临时文件夹
    if chat_id:
        temp_dir = os.path.join('/tmp', chat_id[:8])
    else:
        temp_dir = os.path.join('/tmp', uuid.uuid7().hex[:8])
    skills_dir = os.path.join(temp_dir, 'skills')
    os.makedirs(skills_dir, exist_ok=True)

    # print(f"Initializing skills in temporary directory: {skills_dir}")

    async def _run():
        try:
            async_gen = _yield_mcp_response(chat_model, message_list, mcp_servers, mcp_output_enable, tool_init_params,
                                            source_id, source_type, temp_dir, chat_id)
            async for chunk in async_gen:
                result_queue.put(('data', chunk))
        except Exception as e:
            maxkb_logger.error(f'Exception: {e}', exc_info=True)
            result_queue.put(('error', e))
        finally:
            result_queue.put(('done', None))

    # 在全局循环中调度任务
    asyncio.run_coroutine_threadsafe(_run(), loop)

    while True:
        msg_type, data = result_queue.get()
        if msg_type == 'done':
            # 清理临时文件夹
            shutil.rmtree(temp_dir, ignore_errors=True)
            break
        if msg_type == 'error':
            # 清理临时文件夹
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise data
        yield data


async def anext_async(agen):
    return await agen.__anext__()


target_source_node_mapping = {
    'TOOL': {'tool-lib-node': lambda n: [n.get('properties').get('node_data').get('tool_lib_id')],
             'ai-chat-node': lambda n: [*(n.get('properties').get('node_data').get('mcp_tool_ids') or []),
                                        *(n.get('properties').get('node_data').get('tool_ids') or []),
                                        *(n.get('properties').get('node_data').get('skill_tool_ids') or [])],
             'mcp-node': lambda n: [n.get('properties').get('node_data').get('mcp_tool_id')]
             },
    'MODEL': {'ai-chat-node': lambda n: [n.get('properties').get('node_data').get('model_id')],
              'question-node': lambda n: [n.get('properties').get('node_data').get('model_id')],
              'speech-to-text-node': lambda n: [n.get('properties').get('node_data').get('stt_model_id')],
              'text-to-speech-node': lambda n: [n.get('properties').get('node_data').get('tts_model_id')],
              'image-to-video-node': lambda n: [n.get('properties').get('node_data').get('model_id')],
              'image-generate-node': lambda n: [n.get('properties').get('node_data').get('model_id')],
              'intent-node': lambda n: [n.get('properties').get('node_data').get('model_id')],
              'image-understand-node': lambda n: [n.get('properties').get('node_data').get('model_id')],
              'parameter-extraction-node': lambda n: [n.get('properties').get('node_data').get('model_id')],
              'video-understand-node': lambda n: [n.get('properties').get('node_data').get('model_id')],
              },
    'KNOWLEDGE': {'search-knowledge-node': lambda n: n.get('properties').get('node_data').get('knowledge_id_list')},
    'APPLICATION': {
        'application-node': lambda n: [n.get('properties').get('node_data').get('application_id')]
    }
}


def get_node_handle_callback(source_type, source_id):
    def node_handle_callback(node):
        from system_manage.models.resource_mapping import ResourceMapping
        response = []
        for key, value in target_source_node_mapping.items():
            if node.get('type') in value:
                call = value.get(node.get('type'))
                target_source_id_list = call(node)
                for target_source_id in target_source_id_list:
                    if target_source_id:
                        response.append(ResourceMapping(source_type=source_type, target_type=key, source_id=source_id,
                                                        target_id=target_source_id))
        return response

    return node_handle_callback


def get_workflow_resource(workflow, node_handle):
    response = []
    if 'nodes' in workflow:
        for node in workflow.get('nodes'):
            rs = node_handle(node)
            if rs:
                for r in rs:
                    response.append(r)
            if node.get('type') == 'loop-node':
                r = get_workflow_resource(node.get('properties', {}).get(
                    'node_data', {}).get('loop_body'), node_handle)
                for rn in r:
                    response.append(rn)
        return list({(str(item.target_type) + str(item.target_id)): item for item in response}.values())
    return []


application_instance_field_call_dict = {
    'TOOL': [
        lambda instance: instance.mcp_tool_ids or [],
        lambda instance: instance.skill_tool_ids or [],
        lambda instance: instance.tool_ids or []
    ],
    'MODEL': [
        lambda instance: [instance.model_id] if instance.model_id else [],
        lambda instance: [
            instance.tts_model_id] if instance.tts_model_id else [],
        lambda instance: [
            instance.stt_model_id] if instance.stt_model_id else []
    ]
}
knowledge_instance_field_call_dict = {
    'MODEL': [lambda instance: [instance.embedding_model_id] if instance.embedding_model_id else []],
}


def get_instance_resource(instance, source_type, source_id, instance_field_call_dict):
    response = []
    from system_manage.models.resource_mapping import ResourceMapping
    for target_type, call_list in instance_field_call_dict.items():
        target_id_list = reduce(
            lambda x, y: [*x, *y], [call(instance) for call in call_list], [])
        if target_id_list:
            for target_id in target_id_list:
                response.append(ResourceMapping(source_type=source_type, target_type=target_type, source_id=source_id,
                                                target_id=target_id))
    return response


def save_workflow_mapping(workflow, source_type, source_id, other_resource_mapping=None):
    if not other_resource_mapping:
        other_resource_mapping = []
    from system_manage.models.resource_mapping import ResourceMapping
    from django.db.models import QuerySet
    QuerySet(ResourceMapping).filter(
        source_type=source_type, source_id=source_id).delete()
    resource_mapping_list = get_workflow_resource(workflow,
                                                  get_node_handle_callback(source_type,
                                                                           source_id))
    resource_mapping_list += other_resource_mapping
    if resource_mapping_list:
        QuerySet(ResourceMapping).bulk_create(
            {(str(item.target_type) + str(item.target_id)): item for item in resource_mapping_list}.values())


def get_tool_id_list(workflow):
    _result = []
    for node in workflow.get('nodes', []):
        if node.get('type') == 'tool-lib-node':
            tool_id = node.get('properties', {}).get(
                'node_data', {}).get('tool_lib_id')
            if tool_id:
                _result.append(tool_id)
        elif node.get('type') == 'loop-node':
            r = get_tool_id_list(node.get('properties', {}).get(
                'node_data', {}).get('loop_body', {}))
            for item in r:
                _result.append(item)
        elif node.get('type') == 'ai-chat-node':
            node_data = node.get('properties', {}).get('node_data', {})
            mcp_tool_ids = node_data.get('mcp_tool_ids') or []
            skill_tool_ids = node_data.get('skill_tool_ids') or []
            tool_ids = node_data.get('tool_ids') or []
            for _id in mcp_tool_ids + tool_ids + skill_tool_ids:
                _result.append(_id)
        elif node.get('type') == 'mcp-node':
            mcp_tool_id = node.get('properties', {}).get(
                'node_data', {}).get('mcp_tool_id')
            if mcp_tool_id:
                _result.append(mcp_tool_id)
    return _result
