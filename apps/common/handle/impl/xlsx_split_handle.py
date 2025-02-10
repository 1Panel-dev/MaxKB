# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： xlsx_parse_qa_handle.py
    @date：2024/5/21 14:59
    @desc:
"""
import io
from typing import List

import openpyxl

from common.handle.base_split_handle import BaseSplitHandle
from common.handle.impl.tools import xlsx_embed_cells_images


def post_cell(image_dict, cell_value):
    image = image_dict.get(cell_value, None)
    if image is not None:
        return f'![](/api/image/{image.id})'
    return cell_value.replace('\n', '<br>').replace('|', '&#124;')


def row_to_md(row, image_dict):
    return '| ' + ' | '.join(
        [post_cell(image_dict, str(cell.value if cell.value is not None else '')) if cell is not None else '' for cell
         in row]) + ' |\n'


def handle_sheet(file_name, sheet, image_dict, limit: int):
    rows = sheet.rows
    paragraphs = []
    result = {'name': file_name, 'content': paragraphs}
    try:
        title_row_list = next(rows)
        title_md_content = row_to_md(title_row_list, image_dict)
        title_md_content += '| ' + ' | '.join(
            ['---' if cell is not None else '' for cell in title_row_list]) + ' |\n'
    except Exception as e:
        return result
    if len(title_row_list) == 0:
        return result
    result_item_content = ''
    for row in rows:
        next_md_content = row_to_md(row, image_dict)
        next_md_content_len = len(next_md_content)
        result_item_content_len = len(result_item_content)
        if len(result_item_content) == 0:
            result_item_content += title_md_content
            result_item_content += next_md_content
        else:
            if result_item_content_len + next_md_content_len < limit:
                result_item_content += next_md_content
            else:
                paragraphs.append({'content': result_item_content, 'title': ''})
                result_item_content = title_md_content + next_md_content
    if len(result_item_content) > 0:
        paragraphs.append({'content': result_item_content, 'title': ''})
    return result


class XlsxSplitHandle(BaseSplitHandle):
    def handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer, save_image):
        buffer = get_buffer(file)
        try:
            workbook = openpyxl.load_workbook(io.BytesIO(buffer))
            try:
                image_dict: dict = xlsx_embed_cells_images(io.BytesIO(buffer))
                save_image([item for item in image_dict.values()])
            except Exception as e:
                image_dict = {}
            worksheets = workbook.worksheets
            worksheets_size = len(worksheets)
            return [row for row in
                    [handle_sheet(file.name,
                                  sheet,
                                  image_dict,
                                  limit) if worksheets_size == 1 and sheet.title == 'Sheet1' else handle_sheet(
                        sheet.title, sheet, image_dict, limit) for sheet
                     in worksheets] if row is not None]
        except Exception as e:
            return [{'name': file.name, 'content': []}]

    def get_content(self, file, save_image):
        pass

    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".xlsx"):
            return True
        return False
