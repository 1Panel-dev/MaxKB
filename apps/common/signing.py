# coding=utf-8
"""
    @project: MaxKB
    @Author:  虎虎虎
    @file:    rsa_util.py
    @date:    2026/09/21 13:57
    @desc:
"""
from common.utils.rsa_util import get_key_pair
from django.core import signing


def loads(s: str):
    value = get_key_pair().get('value')
    return signing.loads(s, key=value)


def dumps(obj):
    value = get_key_pair().get('value')
    return signing.dumps(obj, key=value)
