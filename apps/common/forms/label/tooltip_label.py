# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： tooltip_label.py
    @date：2024/8/22 17:19
    @desc:
"""
from common.forms.label.base_label import BaseLabel


class TooltipLabel(BaseLabel):
    def __init__(self, label, tooltip):
        super().__init__('TooltipLabel', label, attrs={'tooltip': tooltip}, props_info={})
