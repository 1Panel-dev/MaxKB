# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： default_base_model_handle.py
    @date：2025/4/15 11:20
    @desc:
"""
from common.database_model_manage.handle.base_handle import IBaseModelHandle


class DefaultBaseModelHandle(IBaseModelHandle):
    def get_model_dict(self):
        return {}
