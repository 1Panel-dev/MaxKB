# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： base_handle.py
    @date：2025/4/15 11:16
    @desc:
"""
from abc import ABC, abstractmethod


class IBaseModelHandle(ABC):
    @abstractmethod
    def get_model_dict(self):
        pass
