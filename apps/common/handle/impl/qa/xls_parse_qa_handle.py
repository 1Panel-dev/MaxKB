# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： xls_parse_qa_handle.py
    @date：2024/5/21 14:59
    @desc:
"""

import xlrd

from common.handle.base_parse_qa_handle import BaseParseQAHandle


def handle_sheet(file_name, sheet):
    rows = iter([sheet.row_values(i) for i in range(sheet.nrows)])
    try:
        title_row_list = next(rows)
    except Exception as e:
        return None
    title_row_index_dict = {'title': 0, 'content': 1, 'problem_list': 2}
    for index in range(len(title_row_list)):
        title_row = str(title_row_list[index])
        if title_row.startswith('分段标题'):
            title_row_index_dict['title'] = index
        if title_row.startswith('分段内容'):
            title_row_index_dict['content'] = index
        if title_row.startswith('问题'):
            title_row_index_dict['problem_list'] = index
    paragraph_list = []
    for row in rows:
        problem = str(row[title_row_index_dict.get('problem_list')])
        problem_list = [{'content': p[0:255]} for p in problem.split('\n') if len(p.strip()) > 0]
        paragraph_list.append({'title': str(row[title_row_index_dict.get('title')])[0:255],
                               'content': str(row[title_row_index_dict.get('content')])[0:4096],
                               'problem_list': problem_list})
    return {'name': file_name, 'paragraphs': paragraph_list}


class XlsParseQAHandle(BaseParseQAHandle):
    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".xls"):
            return True
        return False

    def handle(self, file, get_buffer):
        buffer = get_buffer(file)
        workbook = xlrd.open_workbook(file_contents=buffer)
        worksheets = workbook.sheets()
        worksheets_size = len(worksheets)
        return [row for row in
                [handle_sheet(file.name, sheet) if worksheets_size == 1 and sheet.name == 'Sheet1' else handle_sheet(
                    sheet.name, sheet) for sheet
                 in worksheets] if row is not None]
