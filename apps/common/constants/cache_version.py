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
    WORKSPACE_LIST = "WORKSPACE:LIST", lambda user_id: user_id
    # 用户数据
    USER = "USER", lambda user_id: user_id
    # 当前用户所有的角色
    ROLE_LIST = "ROLE:LIST", lambda user_id: user_id
    # 当前用户所有权限
    PERMISSION_LIST = "PERMISSION:LIST", lambda user_id: user_id
    # 验证码
    CAPTCHA = "CAPTCHA", lambda captcha: captcha
    # 系统
    SYSTEM = "SYSTEM", lambda key: key
    # 应用对接三方应用的缓存
    APPLICATION_THIRD_PARTY = "APPLICATION:THIRD_PARTY", lambda key: key

    # 对话
    CHAT = "CHAT", lambda key: key

    CHAT_INFO = "CHAT_INFO", lambda key: key

    CHAT_VARIABLE = "CHAT_VARIABLE", lambda key: key

    # 应用API KEY
    APPLICATION_API_KEY = "APPLICATION_API_KEY", lambda secret_key, use_get_data: secret_key

    CHAT_USER_TOKEN = "CHAT_USER_TOKEN", lambda token: token

    def get_version(self):
        return self.value[0]

    def get_key_func(self):
        return self.value[1]

    def get_key(self, **kwargs):
        return self.value[1](**kwargs)
