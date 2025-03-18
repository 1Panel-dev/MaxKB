# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： SystemEncoder.py
    @date：2025/3/17 16:38
    @desc:
"""
import datetime
import decimal
import json
import uuid

from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile


class SystemEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, InMemoryUploadedFile):
            return {'name': obj.name, 'size': obj.size}
        if isinstance(obj, TemporaryUploadedFile):
            return {'name': obj.name, 'size': obj.size}
        else:
            return json.JSONEncoder.default(self, obj)
