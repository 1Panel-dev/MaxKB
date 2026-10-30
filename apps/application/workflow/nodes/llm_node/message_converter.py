# coding=utf-8
"""
@project: MaxKB
@Author：虎虎虎
@file： message_converter.py
@date：2026/10/16
@desc: 把上下文变量中的消息列表转换为 LangChain 消息

支持两种元素格式,可混用:
1. 内容项,按 type 区分(其他 type 忽略):
   - SYSTEM     {"type": "SYSTEM", "content": "..."}
   - USER       {"type": "USER", "content": "...", "images": [...], "videos": [...], "files": [...]}
   - ASSISTANT  {"type": "ASSISTANT", "content": "..."}                  模型回答
   - TOOL       {"type": "TOOL", "id": "调用id", "name": "函数名", "arguments": "{...}", "content": "工具结果",
                 "ai_id": "同一次模型回复的id", "reasoning": "...", "reasoning_key": "reasoning_content"}
   type 为 function(LLM 节点 tool_calls 输出)或缺省 type 但带 name / arguments 的元素同样视为 TOOL。
   相邻同类型内容合并为一条消息;相邻且 ai_id 相同的 TOOL 合并为一条带 tool_calls 的 assistant 消息,
   随后每个 TOOL 生成一条 tool 消息。TOOL 字段同时兼容 toolName / functionArguments / aiId / reasoningKey 写法。
2. OpenAI 消息:{"role": "system|user|assistant|tool", "content": ..., "tool_calls": [...], "tool_call_id": "..."}
   以及字符串(视为 user 消息)和 LangChain BaseMessage。
"""

import json

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    convert_to_messages,
)

from application.workflow.nodes.ai_chat_node.ai_chat_node import _process_images
from common.utils.partial_json import parse_partial_json

CONTENT_TYPES = {"SYSTEM", "USER", "ASSISTANT", "TOOL"}
# OpenAI 消息中需要透传给 LangChain 的字段
OPENAI_MESSAGE_KEYS = ("role", "content", "name", "tool_calls", "tool_call_id")
TOOL_NAME_KEYS = ("name", "tool_name", "toolName", "function_name")
TOOL_ARGUMENT_KEYS = ("arguments", "function_arguments", "functionArguments")
# 各家模型输出思考内容的字段名不同,按优先级识别;reasoning_key 输出实际命中的字段,便于下游按原字段回传
REASONING_KEYS = ("reasoning_content", "reasoning", "reasoning_text", "thinking")


def _content_type(item: dict):
    """识别内容项类型;非内容项返回 None"""
    _type = str(item.get("type") or "").upper()
    if _type in CONTENT_TYPES:
        return _type
    # LLM 节点输出的 tool_calls(type=function)及未声明 type 的工具调用
    if _type == "FUNCTION" or (not _type and any(k in item for k in TOOL_NAME_KEYS + TOOL_ARGUMENT_KEYS)):
        return "TOOL"
    return None


def _first(item: dict, *keys, default=None):
    for key in keys:
        value = item.get(key)
        if value is not None:
            return value
    return default


def _text(value) -> str:
    if value is None:
        return ""
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def _parse_arguments(arguments) -> dict:
    if isinstance(arguments, dict):
        return arguments
    try:
        parsed = parse_partial_json(arguments or "{}")
        return parsed if isinstance(parsed, dict) else {}
    except (TypeError, ValueError):
        return {}


def _user_parts(item: dict) -> list:
    parts = []
    images = item.get("images") or []
    parts.extend(_process_images([{"url": i} if isinstance(i, str) else i for i in images]))
    for video in item.get("videos") or []:
        url = video if isinstance(video, str) else (video or {}).get("url")
        if url:
            parts.append({"type": "video_url", "video_url": {"url": url}})
    file_names = [
        (f if isinstance(f, str) else (f or {}).get("name") or (f or {}).get("file_name") or "unknown")
        for f in item.get("files") or []
    ]
    if file_names:
        parts.append({"type": "text", "text": "Files: " + ", ".join(file_names)})
    return parts


class _Converter:
    def __init__(self):
        self.result: list[BaseMessage] = []
        self.system = ""
        self.user = ""
        self.user_parts: list = []
        self.assistant = ""
        self.tool_group: list[dict] = []

    def flush_system(self):
        if self.system:
            self.result.append(SystemMessage(self.system))
            self.system = ""

    def flush_user(self):
        if not self.user and not self.user_parts:
            return
        if self.user_parts:
            text = [{"type": "text", "text": self.user}] if self.user else []
            self.result.append(HumanMessage(content=[*text, *self.user_parts]))
        else:
            self.result.append(HumanMessage(self.user))
        self.user = ""
        self.user_parts = []

    def flush_assistant(self):
        if self.assistant:
            self.result.append(AIMessage(self.assistant))
            self.assistant = ""

    def flush_tools(self):
        if not self.tool_group:
            return
        tool_calls = [
            {
                "id": _text(item.get("id")),
                "name": _text(_first(item, *TOOL_NAME_KEYS)),
                "args": _parse_arguments(_first(item, *TOOL_ARGUMENT_KEYS)),
                "type": "tool_call",
            }
            for item in self.tool_group
        ]
        additional_kwargs = {}
        # 同一次模型回复共享 reasoning,只要声明了 reasoning_key 就保留(空字符串也保留)
        for item in self.tool_group:
            reasoning_key = _first(item, "reasoning_key", "reasoningKey", default="reasoning")
            if reasoning_key:
                additional_kwargs[reasoning_key] = item.get(reasoning_key) or ""
                break
        self.result.append(AIMessage(content="", tool_calls=tool_calls, additional_kwargs=additional_kwargs))
        for item, tool_call in zip(self.tool_group, tool_calls):
            self.result.append(ToolMessage(content=_text(item.get("content")), tool_call_id=tool_call["id"]))
        self.tool_group = []

    def flush_all(self):
        self.flush_tools()
        self.flush_system()
        self.flush_user()
        self.flush_assistant()

    def add_content(self, item: dict, _type: str):
        if _type == "TOOL":
            self.flush_system()
            self.flush_user()
            self.flush_assistant()
            ai_id = _first(item, "ai_id", "aiId")
            if self.tool_group and not (ai_id and ai_id == _first(self.tool_group[0], "ai_id", "aiId")):
                self.flush_tools()
            self.tool_group.append(item)
            return
        content = _text(item.get("content"))
        self.flush_tools()
        if _type == "SYSTEM":
            self.flush_user()
            self.flush_assistant()
            self.system += content
        elif _type == "USER":
            self.flush_system()
            self.flush_assistant()
            self.user += content
            self.user_parts.extend(_user_parts(item))
        elif _type == "ASSISTANT":
            self.flush_system()
            self.flush_user()
            self.assistant += content

    def add_message(self, message: BaseMessage):
        self.flush_all()
        self.result.append(message)

    def convert(self, value) -> list[BaseMessage]:
        for item in value:
            if isinstance(item, BaseMessage):
                self.add_message(item)
            elif isinstance(item, str):
                self.add_message(HumanMessage(item))
            elif isinstance(item, dict):
                if "role" in item:
                    self.add_message(convert_to_messages([{k: item[k] for k in OPENAI_MESSAGE_KEYS if k in item}])[0])
                elif _type := _content_type(item):
                    self.add_content(item, _type)
        self.flush_all()
        return self.result


def to_messages(value) -> list[BaseMessage]:
    """把引用变量里的消息列表转换为 LangChain 消息;非数组或 JSON 字符串解析失败时返回空列表"""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return []
    if not isinstance(value, list):
        return []
    return _Converter().convert(value)


def to_reasoning_chunk(chunk):
    """从分片中取思考内容,返回 (实际使用的字段名, 内容);无思考内容时返回 (None, None)"""
    for key in REASONING_KEYS:
        value = chunk.additional_kwargs.get(key)
        if value:
            return key, value
    return None, None
