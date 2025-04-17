# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： object_card.py
    @date：2023/10/31 18:02
    @desc:
"""
from typing import Dict

from common.forms.base_field import BaseExecField, TriggerType


class ObjectCard(BaseExecField):
    """
    收集对象子表卡片
    """

    def __init__(self,
                 label: str,
                 text_field: str,
                 value_field: str,
                 provider: str,
                 method: str,
                 required: bool = False,
                 default_value: object = None,
                 relation_show_field_dict: Dict = None,
                 relation_trigger_field_dict: Dict = None,
                 trigger_type: TriggerType = TriggerType.OPTION_LIST,
                 attrs: Dict[str, object] = None,
                 props_info: Dict[str, object] = None):
        super().__init__("ObjectCard", label, text_field, value_field, provider, method, required, default_value,
                         relation_show_field_dict, relation_trigger_field_dict, trigger_type, attrs, props_info)
