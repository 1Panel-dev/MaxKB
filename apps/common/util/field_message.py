# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： field_message.py
    @date：2024/3/1 14:30
    @desc:
"""
from django.utils.functional import lazy
from rest_framework import serializers


def value_(field, value):
    return f"【{field}】 {value}"


def reset_messages(field, messages):
    return {key: lazy(value_, str)(field, messages.get(key)) for key in messages}


def reset_message_by_field(field_text, field):
    return reset_messages(field_text, {**field.default_error_messages, **field.__bases__[0].default_error_messages})


class ErrMessage:
    @staticmethod
    def char(field: str):
        return reset_message_by_field(field, serializers.CharField)

    @staticmethod
    def uuid(field: str):
        return reset_messages(field, serializers.UUIDField.default_error_messages)

    @staticmethod
    def integer(field: str):
        return reset_messages(field, serializers.IntegerField.default_error_messages)

    @staticmethod
    def list(field: str):
        return reset_messages(field, serializers.ListField.default_error_messages)

    @staticmethod
    def boolean(field: str):
        return reset_messages(field, serializers.BooleanField.default_error_messages)

    @staticmethod
    def dict(field: str):
        return reset_messages(field, serializers.DictField.default_error_messages)

    @staticmethod
    def float(field: str):
        return reset_messages(field, serializers.FloatField.default_error_messages)

    @staticmethod
    def json(field: str):
        return reset_messages(field, serializers.JSONField.default_error_messages)

    @staticmethod
    def base(field: str):
        return reset_messages(field, serializers.Field.default_error_messages)

    @staticmethod
    def date(field: str):
        return reset_messages(field, serializers.DateField.default_error_messages)

    @staticmethod
    def image(field: str):
        return reset_messages(field, serializers.ImageField.default_error_messages)

    @staticmethod
    def file(field: str):
        return reset_messages(field, serializers.FileField.default_error_messages)
