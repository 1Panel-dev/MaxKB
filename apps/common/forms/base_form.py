# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_form.py
    @date：2023/11/1 16:04
    @desc:
"""
from typing import Dict

from common.forms import BaseField


class BaseForm:
    def to_form_list(self, **kwargs):
        return [{**self.__getattribute__(key).to_dict(**kwargs), 'field': key} for key in
                list(filter(lambda key: isinstance(self.__getattribute__(key), BaseField),
                            [attr for attr in vars(self.__class__) if not attr.startswith("__")]))]

    def valid_form(self, form_data):
        field_keys = list(filter(lambda key: isinstance(self.__getattribute__(key), BaseField),
                                 [attr for attr in vars(self.__class__) if not attr.startswith("__")]))
        for field_key in field_keys:
            self.__getattribute__(field_key).is_valid(form_data.get(field_key))

    def get_default_form_data(self):
        return {key: self.__getattribute__(key).default_value for key in
                [attr for attr in vars(self.__class__) if not attr.startswith("__")] if
                isinstance(self.__getattribute__(key), BaseField) and self.__getattribute__(
                    key).default_value is not None}
