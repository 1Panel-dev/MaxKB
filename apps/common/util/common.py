# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： common.py
    @date：2023/10/16 16:42
    @desc:
"""
from functools import reduce
from typing import Dict


def query_params_to_single_dict(query_params: Dict):
    return reduce(lambda x, y: {**x, y[0]: y[1]}, list(filter(lambda row: row[1] is not None,
                                                              list(map(lambda row: (
                                                                  row[0], row[1][0] if isinstance(row[1][0],
                                                                                                  list) and len(
                                                                      row[1][0]) > 0 else row[1][0]),
                                                                       query_params.items())))), {})
