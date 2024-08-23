# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： base_label.py
    @date：2024/8/22 17:11
    @desc:
"""


class BaseLabel:
    def __init__(self,
                 input_type: str,
                 label: str,
                 attrs=None,
                 props_info=None):
        self.input_type = input_type
        self.label = label
        self.attrs = attrs
        self.props_info = props_info

    def to_dict(self, **kwargs):
        return {
            'input_type': self.input_type,
            'label': self.label,
            'attrs': {} if self.attrs is None else self.attrs,
            'props_info': {} if self.props_info is None else self.props_info,
        }
