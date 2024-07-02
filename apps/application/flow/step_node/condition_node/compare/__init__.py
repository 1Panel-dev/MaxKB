# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： __init__.py.py
    @date：2024/6/7 14:43
    @desc:
"""

from .contain_compare import *
from .equal_compare import *
from .gt_compare import *
from .ge_compare import *
from .le_compare import *
from .lt_compare import *
from .len_ge_compare import *
from .len_gt_compare import *
from .len_le_compare import *
from .len_lt_compare import *
from .len_equal_compare import *
from .is_not_null_compare import *
from .is_null_compare import *
from .not_contain_compare import *

compare_handle_list = [GECompare(), GTCompare(), ContainCompare(), EqualCompare(), LTCompare(), LECompare(),
                       LenLECompare(), LenGECompare(), LenEqualCompare(), LenGTCompare(), LenLTCompare(),
                       IsNullCompare(),
                       IsNotNullCompare(), NotContainCompare()]
