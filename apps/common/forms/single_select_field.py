# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： single_select_field.py
    @date：2023/10/31 18:00
    @desc:
"""
from typing import List, Dict

from common.forms.base_field import TriggerType, BaseExecField


class SingleSelect(BaseExecField):
    """
    下拉单选
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
                 relation_show_field_dict: Dict = None,
                 relation_trigger_field_dict: Dict = None,
                 trigger_type: TriggerType = TriggerType.OPTION_LIST,
                 attrs: Dict[str, object] = None,
                 props_info: Dict[str, object] = None):
        super().__init__("SingleSelect", label, text_field, value_field, provider, method, required, default_value,
                         relation_show_field_dict, relation_trigger_field_dict, trigger_type, attrs, props_info)
        self.option_list = option_list

    def to_dict(self):
        return {**super().to_dict(), 'option_list': self.option_list}
