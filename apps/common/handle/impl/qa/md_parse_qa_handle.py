# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： md_parse_qa_handle.py
    @date：2024/5/21 14:59
    @desc:
"""
import re
import traceback

from charset_normalizer import detect

from common.handle.base_parse_qa_handle import BaseParseQAHandle, get_title_row_index_dict, get_row_value
from common.utils.logger import maxkb_logger


class MarkdownParseQAHandle(BaseParseQAHandle):
    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".md") or file_name.endswith(".markdown"):
            return True
        return False

    def parse_markdown_table(self, content):
        """解析 Markdown 表格,返回表格数据列表"""
        tables = []
        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            # 检测表格开始(包含 | 符号)
            if '|' in line and line.startswith('|'):
                table_data = []
                # 读取表头
                header = [cell.strip() for cell in line.split('|')[1:-1]]
                table_data.append(header)
                i += 1

                # 跳过分隔行 (例如: | --- | --- |)
                if i < len(lines) and re.match(r'\s*\|[\s\-:]+\|\s*', lines[i]):
                    i += 1

                # 读取数据行
                while i < len(lines):
                    line = lines[i].strip()
                    if not line.startswith('|'):
                        break
                    row = [cell.strip() for cell in line.split('|')[1:-1]]
                    if len(row) > 0:
                        table_data.append(row)
                    i += 1

                if len(table_data) > 1:  # 至少有表头和一行数据
                    tables.append(table_data)
            else:
                i += 1

        return tables

    def handle(self, file, get_buffer, save_image):
        buffer = get_buffer(file)
        try:
            # 检测编码并读取文件内容
            encoding = detect(buffer)['encoding']
            content = buffer.decode(encoding if encoding else 'utf-8')

            # 按 sheet 分割内容
            sheet_sections = self.split_by_sheets(content)

            result = []

            for sheet_name, sheet_content in sheet_sections:
                # 解析该 sheet 的表格
                tables = self.parse_markdown_table(sheet_content)

                paragraph_list = []

                # 处理每个表格
                for table in tables:
                    if len(table) < 2:
                        continue

                    title_row_list = table[0]
                    title_row_index_dict = get_title_row_index_dict(title_row_list)

                    # 处理表格的每一行数据
                    for row in table[1:]:
                        content_text = get_row_value(row, title_row_index_dict, 'content')
                        if content_text is None:
                            continue

                        problem = get_row_value(row, title_row_index_dict, 'problem_list')
                        problem = str(problem) if problem is not None else ''
                        problem_list = [{'content': p[0:255]} for p in problem.split('\n') if len(p.strip()) > 0]

                        title = get_row_value(row, title_row_index_dict, 'title')
                        title = str(title) if title is not None else ''

                        paragraph_list.append({
                            'title': title[0:255],
                            'content': content_text[0:102400],
                            'problem_list': problem_list
                        })

                result.append({'name': sheet_name, 'paragraphs': paragraph_list})

            return result if result else [{'name': file.name, 'paragraphs': []}]

        except Exception as e:
            maxkb_logger.error(f"Error processing Markdown file {file.name}: {e}, {traceback.format_exc()}")
            return [{'name': file.name, 'paragraphs': []}]

    def split_by_sheets(self, content):
        """按二级标题(##)分割 sheet"""
        lines = content.split('\n')
        sheets = []
        current_sheet_name = None
        current_content = []

        for line in lines:
            # 检测二级标题作为 sheet 名称
            if line.strip().startswith('## '):
                if current_sheet_name is not None:
                    sheets.append((current_sheet_name, '\n'.join(current_content)))
                current_sheet_name = line.strip()[3:].strip()
                current_content = []
            else:
                current_content.append(line)

        # 添加最后一个 sheet
        if current_sheet_name is not None:
            sheets.append((current_sheet_name, '\n'.join(current_content)))

        # 如果没有找到 sheet 标题,返回整个内容
        if not sheets:
            sheets.append(('default', content))

        return sheets
