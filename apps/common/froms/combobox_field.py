# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： combobox_field.py
    @date：2023/10/31 17:59
    @desc:
"""
from typing import List, Dict

from common.froms.base_field import BaseExecField, TriggerType


class Combobox(BaseExecField):
    """
    多选框
    """

    def __init__(self,
                 label: str,
                 text_field: str,
                 value_field: str,
                 option_list: List[str:object],
                 provider: str = None,
                 method: str = None,
                 required: bool = False,
                 default_value: object = None,
                 relation_show_field_list: List[str] = None,
                 relation_show_value_list: List[str] = None,
                 relation_trigger_field_list: List[str] = None,
                 relation_trigger_value_list: List[str] = None,
                 trigger_type: TriggerType = TriggerType.OPTION_LIST,
                 attrs: Dict[str, object] = None,
                 props_info: Dict[str, object] = None):
        super().__init__("Combobox", label, text_field, value_field, provider, method, required, default_value,
                         relation_show_field_list, relation_show_value_list, relation_trigger_field_list,
                         relation_trigger_value_list, trigger_type, attrs, props_info)
        self.option_list = option_list

    def to_dict(self):
        return {**super().to_dict(), 'option_list': self.option_list}
