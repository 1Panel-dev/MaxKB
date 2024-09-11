# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_parse_qa_handle.py
    @date：2024/5/21 14:56
    @desc:
"""
from abc import ABC, abstractmethod


class BaseParseTableHandle(ABC):
    @abstractmethod
    def support(self, file, get_buffer):
        pass

    @abstractmethod
    def handle(self, file, get_buffer,save_image):
        pass
