# coding=utf-8
"""
@project: MaxKB
@Author:  虎虎虎
@file:    base.py
@date:    2026/9/15
@desc:
"""

from pydantic import create_model


def build_schema(fields: dict):
    return create_model("dynamicSchema", **fields)


def get_type(_type: str):
    if _type == "float":
        return float
    if _type == "string":
        return str
    if _type == "int":
        return int
    if _type == "dict":
        return dict
    if _type == "array":
        return list
    if _type == "boolean":
        return bool
    return object
