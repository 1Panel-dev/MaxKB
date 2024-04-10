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
from docx.table import Table
from docx.text.paragraph import Paragraph

from common.handle.base_split_handle import BaseSplitHandle
from common.util.split_model import SplitModel

default_pattern_list = [re.compile('(?<=^)# .*|(?<=\\n)# .*'),
                        re.compile('(?<=\\n)(?<!#)## (?!#).*|(?<=^)(?<!#)## (?!#).*'),
                        re.compile("(?<=\\n)(?<!#)### (?!#).*|(?<=^)(?<!#)### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)#### (?!#).*|(?<=^)(?<!#)#### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)##### (?!#).*|(?<=^)(?<!#)##### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)###### (?!#).*|(?<=^)(?<!#)###### (?!#).*")]


class DocSplitHandle(BaseSplitHandle):
    @staticmethod
    def paragraph_to_md(paragraph):
        try:
            psn = paragraph.style.name
            if psn.startswith('Heading'):
                return "".join(["#" for i in range(int(psn.replace("Heading ", '')))]) + " " + paragraph.text
        except Exception as e:
            return paragraph.text
        return paragraph.text

    @staticmethod
    def table_to_md(table):
        rows = table.rows
        # 创建 Markdown 格式的表格
        md_table = '| ' + ' | '.join([cell.text.replace("\n", '</br>') for cell in rows[0].cells]) + ' |\n'
        md_table += '| ' + ' | '.join(['---' for i in range(len(rows[0].cells))]) + ' |\n'
        for row in rows[1:]:
            md_table += '| ' + ' | '.join([cell.text.replace("\n", '</br>') for cell in row.cells]) + ' |\n'
        return md_table

    def to_md(self, doc):
        elements = []
        for element in doc.element.body:
            if element.tag.endswith('tbl'):
                # 处理表格
                table = Table(element, doc)
                elements.append(table)
            elif element.tag.endswith('p'):
                # 处理段落
                paragraph = Paragraph(element, doc)
                elements.append(paragraph)

        return "\n".join(
            [self.paragraph_to_md(element) if isinstance(element, Paragraph) else self.table_to_md(element) for element
             in elements])

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
