# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： authenticate.py
    @date：2024/3/14 03:02
    @desc:  认证处理器
"""
from abc import ABC, abstractmethod


class AuthBaseHandle(ABC):
    @abstractmethod
    def support(self, request, token: str, get_token_details):
        pass

    @abstractmethod
    def handle(self, request, token: str, get_token_details):
        pass
