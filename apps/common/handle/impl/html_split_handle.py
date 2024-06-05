# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： html_split_handle.py
    @date：2024/5/23 10:58
    @desc:
"""
import re
from typing import List

from bs4 import BeautifulSoup
from charset_normalizer import detect
from html2text import html2text

from common.handle.base_split_handle import BaseSplitHandle
from common.util.split_model import SplitModel

default_pattern_list = [re.compile('(?<=^)# .*|(?<=\\n)# .*'),
                        re.compile('(?<=\\n)(?<!#)## (?!#).*|(?<=^)(?<!#)## (?!#).*'),
                        re.compile("(?<=\\n)(?<!#)### (?!#).*|(?<=^)(?<!#)### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)#### (?!#).*|(?<=^)(?<!#)#### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)##### (?!#).*|(?<=^)(?<!#)##### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)###### (?!#).*|(?<=^)(?<!#)###### (?!#).*")]


def get_encoding(buffer):
    beautiful_soup = BeautifulSoup(buffer, "html.parser")
    meta_list = beautiful_soup.find_all('meta')
    charset_list = [meta.attrs.get('charset') for meta in meta_list if
                    meta.attrs is not None and 'charset' in meta.attrs]
    if len(charset_list) > 0:
        charset = charset_list[0]
        return charset
    return detect(buffer)['encoding']


class HTMLSplitHandle(BaseSplitHandle):
    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".html"):
            return True
        return False

    def handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer, save_image):
        buffer = get_buffer(file)

        if pattern_list is not None and len(pattern_list) > 0:
            split_model = SplitModel(pattern_list, with_filter, limit)
        else:
            split_model = SplitModel(default_pattern_list, with_filter=with_filter, limit=limit)
        try:
            encoding = get_encoding(buffer)
            content = buffer.decode(encoding)
            content = html2text(content)
        except BaseException as e:
            return {'name': file.name,
                    'content': []}
        return {'name': file.name,
                'content': split_model.parse(content)
                }
