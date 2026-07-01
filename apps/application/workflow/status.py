# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： status.py
    @date：2026/6/30 15:47
    @desc:
"""
from enum import Enum


class Status(Enum):
    # 成功
    SUCCESS = "SUCCESS"
    # 失败
    FAIL = "FAIL"
    # 运行中
    RUNNING = "RUNNING"
    # 运行前
    BEFORE_RUNNING = "BEFORE_RUNNING"
    # 取消
    CANCELLED = "CANCELLED"
