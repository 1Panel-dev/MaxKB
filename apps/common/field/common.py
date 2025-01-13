# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： common.py
    @date：2024/1/11 18:44
    @desc:
"""
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

class ObjectField(serializers.Field):
    def __init__(self, model_type_list, **kwargs):
        self.model_type_list = model_type_list
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        for model_type in self.model_type_list:
            if isinstance(data, model_type):
                return data
        self.fail(_('Message type error'), value=data)

    def to_representation(self, value):
        return value


class InstanceField(serializers.Field):
    def __init__(self, model_type, **kwargs):
        self.model_type = model_type
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if not isinstance(data, self.model_type):
            self.fail(_('Message type error'), value=data)
        return data

    def to_representation(self, value):
        return value


class FunctionField(serializers.Field):

    def to_internal_value(self, data):
        if not callable(data):
            self.fail(_('not a function'), value=data)
        return data

    def to_representation(self, value):
        return value


class UploadedImageField(serializers.ImageField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_representation(self, value):
        return value


class UploadedFileField(serializers.FileField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_representation(self, value):
        return value
