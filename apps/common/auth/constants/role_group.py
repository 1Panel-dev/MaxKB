# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： role_group.py
    @date：2026/8/4 9:57
    @desc:
"""
from enum import Enum


class RoleGroup(Enum):
    # 系统用户
    SYSTEM_USER = "SYSTEM_USER"
    # 对话用户
    CHAT_USER = "CHAT_USER"
