# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： text_input_field.py
    @date：2023/10/31 17:58
    @desc:
"""
from typing import Dict

from common.forms.base_field import BaseField, TriggerType


class TextInputField(BaseField):
    """
    文本输入框
    """

    def __init__(self, label: str,
                 required: bool = False,
                 default_value=None,
                 relation_show_field_dict: Dict = None,

                 attrs=None, props_info=None):
        super().__init__('TextInput', label, required, default_value, relation_show_field_dict,
                         {},
                         TriggerType.OPTION_LIST, attrs, props_info)
