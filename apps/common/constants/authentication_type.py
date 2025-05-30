# coding=utf-8
"""
    @project: maxkb
    @Author：虎虎
    @file： authentication_type.py
    @date：2023/11/14 20:03
    @desc:
"""
from enum import Enum


class AuthenticationType(Enum):
    # 系统用户
    SYSTEM_USER = "SYSTEM_USER"
    # 对话用户
    CHAT_USER = "CHAT_USER"
    # 对话匿名用户
    CHAT_ANONYMOUS_USER = "CHAT_ANONYMOUS_USER"
    # APIKEY
    API_KEY = "API_KEY"
