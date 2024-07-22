# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： base_handle.py
    @date：2024/7/22 17:02
    @desc:
"""
from abc import ABC, abstractmethod


class IBaseModelHandle(ABC):
    @abstractmethod
    def get_model_dict(self):
        pass
