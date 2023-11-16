# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_field.py
    @date：2023/10/31 18:07
    @desc:
"""
from enum import Enum
from typing import List, Dict


class TriggerType(Enum):
    # 执行函数获取 OptionList数据
    OPTION_LIST = 'OPTION_LIST'
    # 执行函数获取子表单
    CHILD_FORMS = 'CHILD_FORMS'


class BaseField:
    def __init__(self,
                 input_type: str,
                 label: str,
                 required: bool = False,
                 default_value: object = None,
                 relation_show_field_list: List[str] = None,
                 relation_show_value_list: List[str] = None,
                 relation_trigger_field_list: List[str] = None,
                 relation_trigger_value_list: List[str] = None,
                 trigger_type: TriggerType = TriggerType.OPTION_LIST,
                 attrs: Dict[str, object] = None,
                 props_info: Dict[str, object] = None):
        """

        :param input_type: 字段
        :param label: 提示
        :param default_value: 默认值
        :param relation_show_field_list:        指定那些当那些字段有值的时候 当前字段显示
        :param relation_show_value_list:        指定字段有值 并且值在relation_show_value_list列表中则显示当前字段
        :param relation_trigger_field_list:     指定那些字段有值的时候 调用当前字段的 执行函数获取optionList数据
        :param relation_trigger_value_list:     指定那些字段有值 并且值在relation_trigger_value_list列表中 则执行函数获取optionList数据
        :param trigger_type:                    执行器类型  OPTION_LIST请求Option_list数据 CHILD_FORMS请求子表单
        :param attrs:                           前端attr数据
        :param props_info:                      其他额外信息
        """
        if props_info is None:
            props_info = {}
        if attrs is None:
            attrs = {}
        self.label = label
        self.attrs = attrs
        self.props_info = props_info
        self.default_value = default_value
        self.input_type = input_type
        self.relation_show_field_list = [] if relation_show_field_list is None else relation_show_field_list
        self.relation_show_value_list = [] if relation_show_value_list is None else relation_show_value_list
        self.relation_trigger_field_list = [] if relation_trigger_field_list is None else relation_trigger_field_list
        self.relation_trigger_value_field_list = [] if relation_trigger_value_list is None else relation_trigger_value_list
        self.required = required
        self.trigger_type = trigger_type

    def to_dict(self):
        return {
            'input_type': self.input_type,
            'label': self.label,
            'required': self.required,
            'default_value': self.default_value,
            'relation_show_field_list': self.relation_show_field_list,
            'relation_show_value_list': self.relation_show_value_list,
            'relation_trigger_field_list': self.relation_trigger_field_list,
            'relation_trigger_value_field_list': self.relation_trigger_value_field_list,
            'trigger_type': self.trigger_type.value,
            'attrs': self.attrs,
            'props_info': self.props_info,
        }


class BaseDefaultOptionField(BaseField):
    def __init__(self, input_type: str,
                 label: str,
                 text_field: str,
                 value_field: str,
                 option_list: List[dict],
                 required: bool = False,
                 default_value: object = None,
                 relation_show_field_list: List[str] = None,
                 relation_show_value_list: List[str] = None,
                 attrs: Dict[str, object] = None,
                 props_info: Dict[str, object] = None):
        """

        :param input_type:           字段
        :param label:           label
        :param text_field:      文本字段
        :param value_field:     值字段
        :param option_list:     可选列表
        :param required:        是否必填
        :param default_value:   默认值
        :param relation_show_field_list:        指定那些当那些字段有值的时候 当前字段显示
        :param relation_show_value_list:        指定字段有值 并且值在relation_show_value_list列表中则显示当前字段
        :param attrs:                           前端attr数据
        :param props_info:                      其他额外信息
        """
        super().__init__(input_type, label, required, default_value, relation_show_field_list, relation_show_value_list,
                         [], [], TriggerType.OPTION_LIST, attrs, props_info)
        self.text_field = text_field
        self.value_field = value_field
        self.option_list = option_list

    def to_dict(self):
        return {**super().to_dict(), 'text_field': self.text_field, 'value_field': self.value_field,
                'option_list': self.option_list}


class BaseExecField(BaseField):
    def __init__(self,
                 input_type: str,
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
        """

        :param input_type:  字段
        :param label:  提示
        :param text_field:  文本字段
        :param value_field: 值字段
        :param provider:    指定供应商
        :param method:      执行供应商函数 method
        :param required:    是否必填
        :param default_value: 默认值
        :param relation_show_field_list:        指定那些当那些字段有值的时候 当前字段显示
        :param relation_show_value_list:        指定字段有值 并且值在relation_show_value_list列表中则显示当前字段
        :param relation_trigger_field_list:     指定那些字段有值的时候 调用当前字段的 执行函数获取optionList数据
        :param relation_trigger_value_list:     指定那些字段有值 并且值在relation_trigger_value_list列表中 则执行函数获取optionList数据
        :param trigger_type:                    执行器类型  OPTION_LIST请求Option_list数据 CHILD_FORMS请求子表单
        :param attrs:                           前端attr数据
        :param props_info:                      其他额外信息
        """
        super().__init__(input_type, label, required, default_value, relation_show_field_list, relation_show_value_list,
                         relation_trigger_field_list, relation_trigger_value_list, trigger_type, attrs, props_info)
        self.text_field = text_field
        self.value_field = value_field
        self.provider = provider
        self.method = method

    def to_dict(self):
        return {**super().to_dict(), 'text_field': self.text_field, 'value_field': self.value_field,
                'provider': self.provider, 'method': self.method}
