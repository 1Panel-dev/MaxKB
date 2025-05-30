"""
    @project: MaxKB
    @Author：虎
    @file： switch_field.py
    @date：2024/10/13 19:43
    @desc:
"""
from typing import Dict
from common.forms import BaseField, TriggerType, BaseLabel


class SwitchField(BaseField):
    """
    滑块输入框
    """

    def __init__(self, label: str or BaseLabel,
                 required: bool = False,
                 default_value=None,
                 relation_show_field_dict: Dict = None,

                 attrs=None, props_info=None):
        """
        @param required:  是否必填
        @param default_value: 默认值
        @param relation_show_field_dict:
        @param attrs:
        @param props_info:
        """

        super().__init__('SwitchInput', label, required, default_value, relation_show_field_dict,
                         {},
                         TriggerType.OPTION_LIST, attrs, props_info)
