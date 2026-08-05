# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： permission_scope_constants.py
    @date：2026/8/4 11:50
    @desc:
"""
from enum import Enum


class PermissionScopeConstants(Enum):
    SYSTEM = 'SYSTEM'
    WORKSPACE = 'WORKSPACE'
    WORKSPACE_RESOURCE = 'WORKSPACE_RESOURCE'
