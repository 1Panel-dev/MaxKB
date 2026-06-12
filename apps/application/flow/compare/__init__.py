# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： __init__.py.py
    @date：2024/6/7 14:43
    @desc:
"""
from typing import List

from .contain_compare import ContainCompare
from .end_with import EndWithCompare
from .equal_compare import EqualCompare
from .ge_compare import GECompare
from .gt_compare import GTCompare
from .is_not_null_compare import IsNotNullCompare
from .is_not_true import IsNotTrueCompare
from .is_null_compare import IsNullCompare
from .is_true import IsTrueCompare
from .le_compare import LECompare
from .len_equal_compare import LenEqualCompare
from .len_ge_compare import LenGECompare
from .len_gt_compare import LenGTCompare
from .len_le_compare import LenLECompare
from .len_lt_compare import LenLTCompare
from .lt_compare import LTCompare
from .not_contain_compare import NotContainCompare
from .not_equal_compare import NotEqualCompare
from .regex_compare import RegexCompare
from .start_with import StartWithCompare
from .wildcard_compare import WildcardCompare

_compare_handler_dict = {
    'is_null': IsNullCompare(),
    'is_not_null': IsNotNullCompare(),
    'contain': ContainCompare(),
    'not_contain': NotContainCompare(),
    'eq': EqualCompare(),
    'not_eq': NotEqualCompare(),
    'ge': GECompare(),
    'gt': GTCompare(),
    'le': LECompare(),
    'lt': LTCompare(),
    'len_eq': LenEqualCompare(),
    'len_ge': LenGECompare(),
    'len_gt': LenGTCompare(),
    'len_le': LenLECompare(),
    'len_lt': LenLTCompare(),
    'is_true': IsTrueCompare(),
    'is_not_true': IsNotTrueCompare(),
    'start_with': StartWithCompare(),
    'end_with': EndWithCompare(),
    'regex': RegexCompare(),
    'wildcard': WildcardCompare(),
}


def _compare(source_value, compare, target_value):
    compare_handler = _compare_handler_dict.get(compare)
    if compare_handler is None:
        raise RuntimeError(f"Unknown compare handler '{compare}'")
    return compare_handler.compare(source_value, compare, target_value)


def _assertion(workflow_manage, field_list: List[str], compare: str, target_value, condition_details: list = None):
    origin_target_value = target_value
    try:
        target_value = workflow_manage.generate_prompt(target_value)
    except Exception:
        pass
    field_value = None
    try:
        field_value = workflow_manage.get_reference_field(field_list[0], field_list[1:])
    except  Exception:
        pass

    result = _compare(field_value, compare, target_value)

    # condition_details不为None，说明调用端需要分支执行详情，拼接到列表中
    if condition_details is not None:
        condition_details.append({
            'field': field_list,
            'field_type': type(field_value).__name__ if field_value is not None else None,
            'field_value': field_value,
            'compare': compare,
            'target_type': type(target_value).__name__ if target_value is not None else None,
            'target_value': target_value,
            'origin_target_value': origin_target_value if origin_target_value != target_value else '',
            'result': result
        })

    return result


def do_assertion(workflow_manage, condition, condition_list, condition_details: list = None):
    b = False if condition == 'and' else True
    for row in condition_list:
        if _assertion(workflow_manage, row.get('field'), row.get('compare'), row.get('value'), condition_details) is b:
            return b
    return not b
