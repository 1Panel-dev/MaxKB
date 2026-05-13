# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： xls_parse_qa_handle.py
    @date：2024/5/21 14:59
    @desc:
"""
import datetime
import traceback
from typing import List

import xlrd
from xlrd.xldate import xldate_as_datetime

from common.handle.base_split_handle import BaseSplitHandle
from common.handle.impl.text.excel_kv_common import (
    make_kv_paragraph,
    normalize_headers,
)
from common.utils.logger import maxkb_logger


def _convert_xlrd_value(workbook, sheet, row_idx: int, col_idx: int):
    """xlrd 把日期读作 float，需要根据 cell type 还原成 datetime。

    其他类型直接返回原值（make_kv_paragraph 内的 normalize_value 会兜底）。
    """
    try:
        cell = sheet.cell(row_idx, col_idx)
    except IndexError:
        return None
    ct = cell.ctype
    if ct == xlrd.XL_CELL_DATE:
        try:
            dt = xldate_as_datetime(cell.value, workbook.datemode)
            return dt
        except Exception:
            return cell.value
    if ct == xlrd.XL_CELL_BOOLEAN:
        return bool(cell.value)
    if ct == xlrd.XL_CELL_EMPTY or ct == xlrd.XL_CELL_BLANK:
        return None
    return cell.value


def handle_sheet(file_name, workbook, sheet, limit: int):
    paragraphs = []
    result = {'name': file_name, 'content': paragraphs}
    if sheet.nrows == 0 or sheet.ncols == 0:
        return result
    try:
        header_values = [_convert_xlrd_value(workbook, sheet, 0, c) for c in range(sheet.ncols)]
        headers = normalize_headers(header_values)
        if not headers:
            return result
        for r in range(1, sheet.nrows):
            row_values = [_convert_xlrd_value(workbook, sheet, r, c) for c in range(sheet.ncols)]
            paragraph = make_kv_paragraph(
                file_name=file_name,
                sheet_name=sheet.name,
                row_idx=r + 1,  # 与 xlsx 一致使用 1-based 行号
                headers=headers,
                row_values=row_values,
                limit=limit,
            )
            if paragraph is not None:
                paragraphs.append(paragraph)
    except Exception as e:
        maxkb_logger.error(f"Error parsing XLS sheet {sheet.name}: {e}, {traceback.format_exc()}")
    return result


class XlsSplitHandle(BaseSplitHandle):
    def handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer, save_image):
        buffer = get_buffer(file)
        try:
            if type(limit) is str:
                limit = int(limit)
            workbook = xlrd.open_workbook(file_contents=buffer)
            worksheets = workbook.sheets()
            worksheets_size = len(worksheets)
            results = []
            for sheet in worksheets:
                # paragraph 内的「文件：xxx」始终用真实文件名（见 xlsx_split_handle 同段说明）
                sheet_result = handle_sheet(file.name, workbook, sheet, limit)
                if worksheets_size == 1 and sheet.name == 'Sheet1':
                    sheet_result['name'] = file.name
                else:
                    sheet_result['name'] = sheet.name
                results.append(sheet_result)
            return [r for r in results if r is not None]
        except Exception as e:
            maxkb_logger.error(f"Error processing XLS file {file.name}: {e}, {traceback.format_exc()}")
            return [{'name': file.name, 'content': []}]

    def get_content(self, file, save_image):
        # 打开 .xls 文件
        try:
            workbook = xlrd.open_workbook(file_contents=file.read(), formatting_info=True)
            sheets = workbook.sheets()
            md_tables = ''
            for sheet in sheets:
                # 过滤空白的sheet
                if sheet.nrows == 0 or sheet.ncols == 0:
                    continue

                # 获取表头和内容
                headers = sheet.row_values(0)
                data = [sheet.row_values(row_idx) for row_idx in range(1, sheet.nrows)]

                # 构建 Markdown 表格
                md_table = '| ' + ' | '.join(headers) + ' |\n'
                md_table += '| ' + ' | '.join(['---'] * len(headers)) + ' |\n'
                for row in data:
                    # 将每个单元格中的内容替换换行符为 <br> 以保留原始格式
                    md_table += '| ' + ' | '.join(
                        [str(cell)
                         .replace('\r\n', '<br>')
                         .replace('\n', '<br>')
                         if cell else '' for cell in row]) + ' |\n'
                md_tables += md_table + '\n\n'

            return md_tables
        except Exception as e:
            maxkb_logger.error(f'excel split handle error: {e}')
            return f'error: {e}'

    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        buffer = get_buffer(file)
        if file_name.endswith(".xls") and xlrd.inspect_format(content=buffer):
            return True
        return False
