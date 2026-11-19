# coding=utf-8
"""
@project: MaxKB
@Author：虎虎虎
@file： content_type.py
@date：2026/6/30 15:57
@desc:
"""

from enum import Enum


class ContentType(Enum):
    TEXT = "TEXT"
    HTML = "HTML"
    REASONING = "REASONING"
    FAILURE = "FAILURE"
    TOOL = "TOOL"
    CONTINUE = "CONTINUE"
    BREAK = "BREAK"
    FORM = "FORM"
    PROGRESS = "PROGRESS"
    # 模型调用的 token 用量，仅供节点内部统计，不输出给前端
    USAGE = "USAGE"
