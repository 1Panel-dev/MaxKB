# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： authentication_type.py
    @date：2023/11/14 20:03
    @desc:
"""
from enum import Enum


class AuthenticationType(Enum):
    # 或者
    USER = "USER"
    # 并且
    APPLICATION_ACCESS_TOKEN = "APPLICATION_ACCESS_TOKEN"
