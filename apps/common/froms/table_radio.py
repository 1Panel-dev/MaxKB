# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： table_radio.py
    @date：2023/10/31 18:01
    @desc:
"""
from typing import List, Dict

from common.froms.base_field import TriggerType, BaseExecField


class TableRadio(BaseExecField):
    """
    table 单选
    """

    def __init__(self,
                 label: str,
                 text_field: str,
                 value_field: str,
                 provider: str,
                 method: str,
                 required: bool = False,
                 default_value: object = None,
                 relation_show_field_list: List[str] = None,
                 relation_show_value_list: List[str] = None,
                 relation_trigger_field_list: List[str] = None,
                 relation_trigger_value_list: List[str] = None,
                 trigger_type: TriggerType = TriggerType.OPTION_LIST,
                 attrs: Dict[str, object] = None,
                 props_info: Dict[str, object] = None):
        super().__init__("TableRadio", label, text_field, value_field, provider, method, required, default_value,
                         relation_show_field_list, relation_show_value_list, relation_trigger_field_list,
                         relation_trigger_value_list, trigger_type, attrs, props_info)
