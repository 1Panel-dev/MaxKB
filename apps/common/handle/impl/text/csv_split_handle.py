# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： csv_parse_qa_handle.py
    @date：2024/5/21 14:59
    @desc:
"""
import csv
import io
import os
import traceback
from typing import List

from charset_normalizer import detect

from common.handle.base_split_handle import BaseSplitHandle
from common.handle.impl.text.excel_kv_common import (
    make_kv_paragraph,
    normalize_headers,
)
from common.utils.logger import maxkb_logger


class CsvSplitHandle(BaseSplitHandle):
    def handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer, save_image):
        buffer = get_buffer(file)
        paragraphs = []
        file_name = os.path.basename(file.name)
        result = {'name': file_name, 'content': paragraphs}
        try:
            if type(limit) is str:
                limit = int(limit)
            encoding = (detect(buffer) or {}).get('encoding') or 'utf-8'
            reader = csv.reader(io.TextIOWrapper(io.BytesIO(buffer), encoding=encoding))
            try:
                header_row = next(reader)
            except StopIteration:
                return result
            headers = normalize_headers(header_row)
            if not headers:
                return result
            # CSV 没有 sheet 概念，sheet_name=None
            for row_idx, row in enumerate(reader, start=2):
                paragraph = make_kv_paragraph(
                    file_name=file_name,
                    sheet_name=None,
                    row_idx=row_idx,
                    headers=headers,
                    row_values=row,
                    limit=limit,
                )
                if paragraph is not None:
                    paragraphs.append(paragraph)
            return result
        except Exception as e:
            maxkb_logger.error(f"Error processing CSV file {file.name}: {e}, {traceback.format_exc()}")
            return result

    def get_content(self, file, save_image):
        buffer = file.read()
        try:
            reader = csv.reader(io.TextIOWrapper(io.BytesIO(buffer), encoding=detect(buffer)['encoding']))
            rows = list(reader)

            if not rows:
                return ""

            # 构建 Markdown 表格
            md_lines = []

            # 添加表头
            header = [cell.replace('\n', '<br>').replace('\r', '') for cell in rows[0]]
            md_lines.append('| ' + ' | '.join(header) + ' |')

            # 添加分隔线
            md_lines.append('| ' + ' | '.join(['---'] * len(header)) + ' |')

            # 添加数据行
            for row in rows[1:]:
                if row:  # 跳过空行
                    # 确保行长度与表头一致,并将换行符转换为 <br>
                    padded_row = [
                                     cell.replace('\n', '<br>').replace('\r', '') for cell in row
                                 ] + [''] * (len(header) - len(row))
                    md_lines.append('| ' + ' | '.join(padded_row[:len(header)]) + ' |')

            return '\n'.join(md_lines)

        except Exception as e:
            maxkb_logger.error(f"Error processing CSV file {file.name}: {e}, {traceback.format_exc()}")
            return ""

    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".csv"):
            return True
        return False
