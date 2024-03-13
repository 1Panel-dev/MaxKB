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
    # 普通用户
    USER = "USER"
    # 公共访问链接
    APPLICATION_ACCESS_TOKEN = "APPLICATION_ACCESS_TOKEN"
    # key API
    API_KEY = "API_KEY"
