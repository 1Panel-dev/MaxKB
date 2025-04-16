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
    # 当前用户所有的角色
    ROLE_LIST = "ROLE::LIST", lambda user_id: user_id
    # 当前用户所有权限
    PERMISSION_LIST = "PERMISSION::LIST", lambda user_id: user_id

    def get_version(self):
        return self.value[0]

    def get_key_func(self):
        return self.value[1]

    def get_key(self, **kwargs):
        return self.value[1](**kwargs)
