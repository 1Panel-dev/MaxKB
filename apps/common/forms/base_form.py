# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_form.py
    @date：2023/11/1 16:04
    @desc:
"""
from common.forms import BaseField


class BaseForm:
    def to_form_list(self):
        return [{**self.__getattribute__(key).to_dict(), 'field': key} for key in
                list(filter(lambda key: isinstance(self.__getattribute__(key), BaseField),
                            [attr for attr in vars(self.__class__) if not attr.startswith("__")]))]
