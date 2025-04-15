# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： cache_version.py
    @date：2025/4/14 19:09
    @desc:
"""
from enum import Enum


class Cache_Version(Enum):
    # 令牌
    TOKEN = "TOKEN", lambda token: token
    # 工作空间列表
    WORKSPACE_LIST = "WORKSPACE::LIST", lambda user_id: user_id
    # 用户数据
    USER = "USER", lambda user_id: user_id
    # 当前用户在当前工作空间的角色列表+本身的角色
    ROLE_LIST = "ROLE::LIST", lambda user_id, workspace_id: f"{user_id}::{workspace_id}"
    # 当前用户在当前工作空间的权限列表+本身的权限列表
    PERMISSION_LIST = "PERMISSION::LIST", lambda user_id, workspace_id: f"{user_id}::{workspace_id}"


version, get_key = Cache_Version.TOKEN.value
