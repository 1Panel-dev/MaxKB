# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： text_split_handle.py
    @date：2024/3/27 18:19
    @desc:
"""
import io
import re
from typing import List

from docx import Document

from common.handle.base_split_handle import BaseSplitHandle
from common.util.split_model import SplitModel

default_pattern_list = [re.compile('(?<=^)# .*|(?<=\\n)# .*'), re.compile('(?<!#)## (?!#).*'),
                        re.compile("(?<!#)### (?!#).*"),
                        re.compile("(?<!#)#### (?!#).*"), re.compile("(?<!#)##### (?!#).*"),
                        re.compile("(?<!#)###### (?!#).*"), re.compile("(?<!\n)\n\n+")]


class DocSplitHandle(BaseSplitHandle):
    @staticmethod
    def paragraph_to_md(paragraph):
        psn = paragraph.style.name
        if psn.startswith('Heading'):
            try:
                return "".join(["#" for i in range(int(psn.replace("Heading ", '')))]) + " " + paragraph.text
            except Exception as e:
                return paragraph.text
        return paragraph.text

    def to_md(self, doc):
        ps = doc.paragraphs
        return "\n".join([self.paragraph_to_md(para) for para in ps])

    def handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer):
        try:
            buffer = get_buffer(file)
            doc = Document(io.BytesIO(buffer))
            content = self.to_md(doc)
            if pattern_list is not None and len(pattern_list) > 0:
                split_model = SplitModel(pattern_list, with_filter, limit)
            else:
                split_model = SplitModel(default_pattern_list, with_filter=with_filter, limit=limit)
        except BaseException as e:
            return {'name': file.name,
                    'content': []}
        return {'name': file.name,
                'content': split_model.parse(content)
                }

    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".docx") or file_name.endswith(".doc"):
            return True
        return False
