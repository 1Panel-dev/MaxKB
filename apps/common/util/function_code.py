# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： function_code.py
    @date：2024/8/7 16:11
    @desc:
"""

from collections import OrderedDict


def exec_code(code_str, keywords):
    local_v = OrderedDict()
    globals_v = globals().copy()
    exec(code_str, globals_v, local_v)
    for local in local_v:
        globals_v[local] = local_v[local]
    f_name, f = local_v.popitem()
    result = f(**keywords)
    globals_v.clear()
    local_v.clear()
    return result

