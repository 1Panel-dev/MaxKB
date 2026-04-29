# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： lt_compare.py
    @date：2024/6/11 9:52
    @desc: 大于比较器
"""
from .compare import Compare


class LenGTCompare(Compare):

    def compare(self, source_value, compare, target_value):
        # 获取target_value的长度
        try:
            target_length = int(target_value)
        except Exception:
            return False

        # 获取source_value的长度
        try:
            source_length = 0 if source_value is None else len(source_value)
        except Exception:
            # 可计算数字长度
            source_length = len(str(source_value))

        # 长度大于比较
        return source_length > target_length
