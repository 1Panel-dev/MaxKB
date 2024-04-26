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
import traceback
import uuid
from typing import List

from docx import Document, ImagePart
from docx.table import Table
from docx.text.paragraph import Paragraph

from common.handle.base_split_handle import BaseSplitHandle
from common.util.split_model import SplitModel
from dataset.models import Image

default_pattern_list = [re.compile('(?<=^)# .*|(?<=\\n)# .*'),
                        re.compile('(?<=\\n)(?<!#)## (?!#).*|(?<=^)(?<!#)## (?!#).*'),
                        re.compile("(?<=\\n)(?<!#)### (?!#).*|(?<=^)(?<!#)### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)#### (?!#).*|(?<=^)(?<!#)#### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)##### (?!#).*|(?<=^)(?<!#)##### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)###### (?!#).*|(?<=^)(?<!#)###### (?!#).*")]


def image_to_mode(image, doc: Document, images_list, get_image_id):
    for img_id in image.xpath('.//a:blip/@r:embed'):  # 获取图片id
        part = doc.part.related_parts[img_id]  # 根据图片id获取对应的图片
        if isinstance(part, ImagePart):
            image_uuid = get_image_id(img_id)
            if len([i for i in images_list if i.id == image_uuid]) == 0:
                image = Image(id=image_uuid, image=part.blob, image_name=part.filename)
                images_list.append(image)
            return f'![](/api/image/{image_uuid})'


def get_paragraph_element_txt(paragraph_element, doc: Document, images_list, get_image_id):
    try:
        images = paragraph_element.xpath(".//pic:pic")
        if len(images) > 0:
            return "".join(
                [item for item in [image_to_mode(image, doc, images_list, get_image_id) for image in images] if
                 item is not None])
        elif paragraph_element.text is not None:
            return paragraph_element.text
        return ""
    except Exception as e:
        print(e)
    return ""


def get_paragraph_txt(paragraph: Paragraph, doc: Document, images_list, get_image_id):
    try:
        return "".join([get_paragraph_element_txt(e, doc, images_list, get_image_id) for e in paragraph._element])
    except Exception as e:
        return ""


def get_cell_text(cell, doc: Document, images_list, get_image_id):
    try:
        return "".join(
            [get_paragraph_txt(paragraph, doc, images_list, get_image_id) for paragraph in cell.paragraphs]).replace(
            "\n", '</br>')
    except Exception as e:
        return ""


def get_image_id_func():
    image_map = {}

    def get_image_id(image_id):
        _v = image_map.get(image_id)
        if _v is None:
            image_map[image_id] = uuid.uuid1()
            return image_map.get(image_id)
        return _v

    return get_image_id


class DocSplitHandle(BaseSplitHandle):
    @staticmethod
    def paragraph_to_md(paragraph: Paragraph, doc: Document, images_list, get_image_id):
        try:
            psn = paragraph.style.name
            if psn.startswith('Heading'):
                return "".join(["#" for i in range(int(psn.replace("Heading ", '')))]) + " " + paragraph.text
        except Exception as e:
            return paragraph.text
        return get_paragraph_txt(paragraph, doc, images_list, get_image_id)

    @staticmethod
    def table_to_md(table, doc: Document, images_list, get_image_id):
        rows = table.rows

        # 创建 Markdown 格式的表格
        md_table = '| ' + ' | '.join(
            [get_cell_text(cell, doc, images_list, get_image_id) for cell in rows[0].cells]) + ' |\n'
        md_table += '| ' + ' | '.join(['---' for i in range(len(rows[0].cells))]) + ' |\n'
        for row in rows[1:]:
            md_table += '| ' + ' | '.join(
                [get_cell_text(cell, doc, images_list, get_image_id) for cell in row.cells]) + ' |\n'
        return md_table

    def to_md(self, doc, images_list, get_image_id):
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
            [self.paragraph_to_md(element, doc, images_list, get_image_id) if isinstance(element,
                                                                                         Paragraph) else self.table_to_md(
                element,
                doc,
                images_list, get_image_id)
             for element
             in elements])

    def handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer, save_image):
        try:
            image_list = []
            buffer = get_buffer(file)
            doc = Document(io.BytesIO(buffer))
            content = self.to_md(doc, image_list, get_image_id_func())
            if len(image_list) > 0:
                save_image(image_list)
            if pattern_list is not None and len(pattern_list) > 0:
                split_model = SplitModel(pattern_list, with_filter, limit)
            else:
                split_model = SplitModel(default_pattern_list, with_filter=with_filter, limit=limit)
        except BaseException as e:
            traceback.print_exception(e)
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
