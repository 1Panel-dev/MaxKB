# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： xls_parse_qa_handle.py
    @date：2024/5/21 14:59
    @desc:
"""
from typing import List

import xlrd

from common.handle.base_split_handle import BaseSplitHandle


def post_cell(cell_value):
    return cell_value.replace('\r\n', '<br>').replace('\n', '<br>').replace('|', '&#124;')


def row_to_md(row):
    return '| ' + ' | '.join(
        [post_cell(str(cell)) if cell is not None else '' for cell in row]) + ' |\n'


def handle_sheet(file_name, sheet, limit: int):
    rows = iter([sheet.row_values(i) for i in range(sheet.nrows)])
    paragraphs = []
    result = {'name': file_name, 'content': paragraphs}
    try:
        title_row_list = next(rows)
        title_md_content = row_to_md(title_row_list)
        title_md_content += '| ' + ' | '.join(
            ['---' if cell is not None else '' for cell in title_row_list]) + ' |\n'
    except Exception as e:
        return result
    if len(title_row_list) == 0:
        return result
    result_item_content = ''
    for row in rows:
        next_md_content = row_to_md(row)
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


class XlsSplitHandle(BaseSplitHandle):
    def handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer, save_image):
        buffer = get_buffer(file)
        try:
            workbook = xlrd.open_workbook(file_contents=buffer)
            worksheets = workbook.sheets()
            worksheets_size = len(worksheets)
            return [row for row in
                    [handle_sheet(file.name,
                                  sheet, limit) if worksheets_size == 1 and sheet.name == 'Sheet1' else handle_sheet(
                        sheet.name, sheet, limit) for sheet
                     in worksheets] if row is not None]
        except Exception as e:
            return [{'name': file.name, 'content': []}]

    def get_content(self, file, save_image):
        pass

    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        buffer = get_buffer(file)
        if file_name.endswith(".xls") and xlrd.inspect_format(content=buffer):
            return True
        return False
