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


def strip_nul(obj):
    if isinstance(obj, str):
        return obj.replace('\x00', '')  # 注意是 '\x00'，真正的空字符
    if isinstance(obj, dict):
        return {k: strip_nul(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [strip_nul(x) for x in obj]
    return obj


class SystemEncoder(json.JSONEncoder):
    def encode(self, obj):
        # 先序列化为字符串
        r = obj
        try:
            r = strip_nul(obj)
        except:
            pass
        json_str = super().encode(strip_nul(r))
        return json_str

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
