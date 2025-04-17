# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： password_input.py
    @date：2023/11/1 14:48
    @desc:
"""
from typing import Dict

from common.forms import BaseField, TriggerType


class PasswordInputField(BaseField):
    """
    文本输入框
    """

    def __init__(self, label: str,
                 required: bool = False,
                 default_value=None,
                 relation_show_field_dict: Dict = None,
                 attrs=None, props_info=None):
        super().__init__('PasswordInput', label, required, default_value, relation_show_field_dict,
                         {},
                         TriggerType.OPTION_LIST, attrs, props_info)
