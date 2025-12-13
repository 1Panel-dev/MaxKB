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
from common.utils.logger import maxkb_logger


def post_cell(cell_value):
    return cell_value.replace('\n', '<br>').replace('|', '&#124;')


def row_to_md(row):
    return '| ' + ' | '.join(
        [post_cell(cell) if cell is not None else '' for cell in row]) + ' |\n'


class CsvSplitHandle(BaseSplitHandle):
    def handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer, save_image):
        buffer = get_buffer(file)
        paragraphs = []
        file_name = os.path.basename(file.name)
        result = {'name': file_name, 'content': paragraphs}
        try:
            if type(limit) is str:
                limit = int(limit)
            reader = csv.reader(io.TextIOWrapper(io.BytesIO(buffer), encoding=detect(buffer)['encoding']))
            try:
                title_row_list = reader.__next__()
                title_md_content = row_to_md(title_row_list)
                title_md_content += '| ' + ' | '.join(
                    ['---' if cell is not None else '' for cell in title_row_list]) + ' |\n'
            except Exception as e:
                return result
            if len(title_row_list) == 0:
                return result
            result_item_content = ''
            for row in reader:
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
