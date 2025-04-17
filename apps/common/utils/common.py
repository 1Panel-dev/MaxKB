# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： common.py
    @date：2025/4/14 18:23
    @desc:
"""
import hashlib
import random
from typing import List


def password_encrypt(row_password):
    """
    密码 md5加密
    :param row_password: 密码
    :return:  加密后密码
    """
    md5 = hashlib.md5()  # 2，实例化md5() 方法
    md5.update(row_password.encode())  # 3，对字符串的字节类型加密
    result = md5.hexdigest()  # 4，加密
    return result


def group_by(list_source: List, key):
    """
    將數組分組
    :param list_source: 需要分組的數組
    :param key: 分組函數
    :return: key->[]
    """
    result = {}
    for e in list_source:
        k = key(e)
        array = result.get(k) if k in result else []
        array.append(e)
        result[k] = array
    return result


CHAR_SET = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


def get_random_chars(number=6):
    return "".join([CHAR_SET[random.randint(0, len(CHAR_SET) - 1)] for index in range(number)])
