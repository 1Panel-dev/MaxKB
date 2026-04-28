# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： __init__.py.py
    @date：2024/6/7 14:43
    @desc:
"""

from .contain_compare import *
from .end_with import EndWithCompare
from .equal_compare import *
from .ge_compare import *
from .gt_compare import *
from .is_not_null_compare import *
from .is_not_true import IsNotTrueCompare
from .is_null_compare import *
from .is_true import IsTrueCompare
from .le_compare import *
from .len_equal_compare import *
from .len_ge_compare import *
from .len_gt_compare import *
from .len_le_compare import *
from .len_lt_compare import *
from .lt_compare import *
from .not_contain_compare import *
from .not_equal_compare import *
from .regex_compare import RegexCompare
from .start_with import StartWithCompare
from .wildcard_compare import WildcardCompare

_compare_handle_dict = {
    'is_null': IsNullCompare(),
    'is_not_null': IsNotNullCompare(),
    'contain': ContainCompare(),
    'not_contain': NotContainCompare(),
    'eq': EqualCompare(),
    'not_eq': NotEqualCompare(),
    'ge': GECompare(),
    'gt': GTCompare(),
    'lt': LTCompare(),
    'le': LECompare(),
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


def _do_compare(source_value, compare, target_value):
    compare_handle = _compare_handle_dict.get(compare)
    if compare_handle:
        return compare_handle.compare(source_value, compare, target_value)
    return False


def do_assertion(workflow_manage, field_list: List[str], compare: str, value):
    try:
        value = workflow_manage.generate_prompt(value)
    except Exception:
        pass
    field_value = None
    try:
        field_value = workflow_manage.get_reference_field(field_list[0], field_list[1:])
    except  Exception:
        pass
    return _do_compare(field_value, compare, value)
