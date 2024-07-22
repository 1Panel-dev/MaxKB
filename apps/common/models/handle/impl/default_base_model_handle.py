# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： default_base_model_handle.py
    @date：2024/7/22 17:06
    @desc:
"""
from common.models.handle.base_handle import IBaseModelHandle


class DefaultBaseModelHandle(IBaseModelHandle):
    def get_model_dict(self):
        return {}
