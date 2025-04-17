# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： slider_field.py
    @date：2024/8/22 17:06
    @desc:
"""
from typing import Dict

from common.exception.app_exception import AppApiException
from common.forms import BaseField, TriggerType, BaseLabel
from django.utils.translation import gettext_lazy as _


class SliderField(BaseField):
    """
    滑块输入框
    """

    def __init__(self, label: str or BaseLabel,
                 _min,
                 _max,
                 _step,
                 precision,
                 required: bool = False,
                 default_value=None,
                 relation_show_field_dict: Dict = None,
                 attrs=None, props_info=None):
        """
        @param label: 提示
        @param _min:  最小值
        @param _max:  最大值
        @param _step: 步长
        @param precision: 保留多少小数
        @param required:  是否必填
        @param default_value: 默认值
        @param relation_show_field_dict:
        @param attrs:
        @param props_info:
        """
        _attrs = {'min': _min, 'max': _max, 'step': _step,
                  'precision': precision, 'show-input-controls': False, 'show-input': True}
        if attrs is not None:
            _attrs.update(attrs)
        super().__init__('Slider', label, required, default_value, relation_show_field_dict,
                         {},
                         TriggerType.OPTION_LIST, _attrs, props_info)

    def is_valid(self, value):
        super().is_valid(value)
        field_label = self.label.label if hasattr(self.label, 'to_dict') else self.label
        if value is not None:
            if value < self.attrs.get('min'):
                raise AppApiException(500,
                                      _("The {field_label} cannot be less than {min}").format(field_label=field_label,
                                                                                              min=self.attrs.get(
                                                                                                  'min')))

            if value > self.attrs.get('max'):
                raise AppApiException(500,
                                      _("The {field_label} cannot be greater than {max}").format(
                                          field_label=field_label,
                                          max=self.attrs.get(
                                              'max')))
