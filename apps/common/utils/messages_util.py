# coding=utf-8
"""
@project: MaxKB
@Author:  虎虎虎
@file:    messages_util.py
@date:    2023/9/11 11:45
@desc:    ChatRecord 存储的 question / messages 与 LangChain 消息之间的转换工具
"""

import json

import uuid_utils.compat as uuid
from django.utils.translation import gettext as _
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage


def to_human_message_list(question):
    """
    将用户消息转换为 HumanMessage 列表。
    question 为 {content, image_list, ...} 结构，历史上下文只取文本部分。
    """
    question = question if isinstance(question, dict) else {"content": question or ""}
    return [HumanMessage(content=question.get("content", "") or "")]


def to_ai_message_list(messages):
    """
    将 messages 中的 TEXT / TOOL 内容块转换为 LangChain 消息列表。
    REASONING/FORM/FAILURE 不进历史；按顺序保留交错。
    注意：type 用字面量，避免对 application.workflow.ContentType 产生反向依赖。
    """
    ai_message_list = []
    for m in messages or []:
        if not isinstance(m, dict):
            continue
        m_type = m.get("type")
        if m_type == "TEXT":
            if m.get("content"):
                ai_message_list.append(AIMessage(content=m.get("content")))
        elif m_type == "TOOL":
            # 工具调用按 OpenAI/LangChain 协议拆成两条消息：
            # 1. AIMessage 携带 tool_calls（名称 + 入参）
            # 2. ToolMessage 携带结果，通过 tool_call_id 与上一条对应
            tool_name = m.get("content")
            if not tool_name:
                continue
            # arguments 存储为 JSON 字符串，需还原为 dict 供 tool_calls 使用
            raw_arguments = m.get("arguments")
            try:
                args = json.loads(raw_arguments) if isinstance(raw_arguments, str) and raw_arguments else {}
            except (json.JSONDecodeError, ValueError):
                args = {}
            if not isinstance(args, dict):
                args = {"arguments": args}
            # tool_call_id 必须让 AIMessage 与 ToolMessage 一一对应，否则模型侧会报错
            tool_call_id = m.get("id") or str(uuid.uuid7())
            ai_message_list.append(
                AIMessage(
                    content="",
                    tool_calls=[{"name": tool_name, "args": args, "id": tool_call_id, "type": "tool_call"}],
                )
            )
            ai_message_list.append(ToolMessage(content=m.get("result") or "", tool_call_id=tool_call_id))
    if len(ai_message_list) == 0:
        ai_message_list = [
            AIMessage(
                content=_(
                    "Sorry, no relevant content was found. Please re-describe your problem or provide more information. "
                )
            )
        ]
    return ai_message_list
