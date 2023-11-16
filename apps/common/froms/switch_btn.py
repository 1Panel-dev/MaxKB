# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： switch_btn.py
    @date：2023/10/31 18:00
    @desc:
"""
from typing import List

from common.froms.base_field import TriggerType, BaseField


class SwitchBtn(BaseField):
    """
    开关
    """

    def __init__(self,
                 label: str,
                 required: bool = False,
                 default_value=None,
                 relation_show_field_list: List[str] = None,
                 relation_show_value_list: List[str] = None,
                 attrs=None, props_info=None):
        super().__init__('SwitchBtn', label, required, default_value, relation_show_field_list,
                         relation_show_value_list, [], [],
                         TriggerType.OPTION_LIST, attrs, props_info)
