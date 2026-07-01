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
    REASONING = "REASONING"
    FAILURE = "FAILURE"
    TOOL = "TOOL"
    CONTINUE = "CONTINUE"
    BREAK = "BREAK"
    FORM = "FORM"
