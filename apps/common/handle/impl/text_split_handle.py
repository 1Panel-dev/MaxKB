# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： text_split_handle.py
    @date：2024/3/27 18:19
    @desc:
"""
import re
from typing import List

from charset_normalizer import detect

from common.handle.base_split_handle import BaseSplitHandle
from common.util.split_model import SplitModel

default_pattern_list = [re.compile('(?<=^)# .*|(?<=\\n)# .*'), re.compile('(?<!#)## (?!#).*'),
                        re.compile("(?<!#)### (?!#).*"),
                        re.compile("(?<!#)#### (?!#).*"), re.compile("(?<!#)##### (?!#).*"),
                        re.compile("(?<!#)###### (?!#).*"), re.compile("(?<!\n)\n\n+")]


class TextSplitHandle(BaseSplitHandle):
    def support(self, file, get_buffer):
        buffer = get_buffer(file)
        file_name: str = file.name.lower()
        if file_name.endswith(".md") or file_name.endswith('.txt'):
            return True
        result = detect(buffer)
        if result['encoding'] != 'ascii' and result['confidence'] > 0.5:
            return True
        return False

    def handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer):
        buffer = get_buffer(file)
        if pattern_list is not None and len(pattern_list) > 0:
            split_model = SplitModel(pattern_list, with_filter, limit)
        else:
            split_model = SplitModel(default_pattern_list, with_filter=with_filter, limit=limit)
        try:
            content = buffer.decode(detect(buffer)['encoding'])
        except BaseException as e:
            return {'name': file.name,
                    'content': []}
        return {'name': file.name,
                'content': split_model.parse(content)
                }
