# coding=utf-8
"""
@project: maxkb
@Author：虎
@file： xlsx_parse_qa_handle.py
@date：2024/5/21 14:59
@desc:
"""

import io
import traceback
from typing import List

from openpyxl import load_workbook

from common.handle.base_split_handle import BaseSplitHandle
from common.handle.impl.common_handle import validate_xlsx_buffer
from common.handle.impl.xlsx_utils import cell_content, iter_sheet_content_rows, load_images, merged_row_values
from common.utils.logger import maxkb_logger

splitter = "\n`-----------------------------------`\n"


def row_to_md(row, image_dict, drawings):
    values = (cell_content(cell.value, image_dict, drawings.get((cell.row, cell.column))) for cell in row)
    return (
        "| "
        + " | ".join(str(v if v is not None else "").replace("\n", "<br>").replace("|", "&#124;") for v in values)
        + " |\n"
    )


def handle_sheet(file_name, sheet, image_dict, limit: int, drawings):
    rows = iter_sheet_content_rows(sheet, drawings=drawings)
    paragraphs = []
    result = {"name": file_name, "content": paragraphs}
    title_row = next(rows, None)
    if not title_row:
        return result
    title_md_content = row_to_md(title_row, image_dict, drawings)
    title_md_content += "| " + " | ".join(["---"] * len(title_row)) + " |\n"
    result_item_content = ""
    for row in rows:
        next_md_content = row_to_md(row, image_dict, drawings)
        next_md_content_len = len(next_md_content)
        result_item_content_len = len(result_item_content)
        if len(result_item_content) == 0:
            result_item_content += title_md_content
            result_item_content += next_md_content
        else:
            if result_item_content_len + next_md_content_len < limit:
                result_item_content += next_md_content
            else:
                paragraphs.append({"content": result_item_content, "title": ""})
                result_item_content = title_md_content + next_md_content
    if len(result_item_content) > 0:
        paragraphs.append({"content": result_item_content, "title": ""})
    elif drawings:
        paragraphs.append({"content": title_md_content, "title": ""})
    return result


class XlsxSplitHandle(BaseSplitHandle):
    def handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer, save_image):
        buffer = get_buffer(file)
        try:
            validate_xlsx_buffer(io.BytesIO(buffer))
            if type(limit) is str:
                limit = int(limit)
            workbook = load_workbook(io.BytesIO(buffer))
            image_dict, drawings = load_images(io.BytesIO(buffer), workbook, save_image)
            return [
                handle_sheet(
                    file.name if len(workbook.worksheets) == 1 and sheet.title == "Sheet1" else sheet.title,
                    sheet,
                    image_dict,
                    limit,
                    drawings.get(sheet.title, {}),
                )
                for sheet in workbook.worksheets
            ]
        except Exception as e:
            maxkb_logger.error(f"Error processing XLSX file {file.name}: {e}, {traceback.format_exc()}")
            return [{"name": file.name, "content": []}]

    def get_content(self, file, save_image):
        try:
            # 加载 Excel 文件
            validate_xlsx_buffer(file)
            workbook = load_workbook(file)
            image_dict, drawings = load_images(file, workbook, save_image)
            tables = []
            for sheet in workbook.worksheets:
                sheet_drawings = drawings.get(sheet.title, {})
                rows = iter_sheet_content_rows(sheet, drawings=sheet_drawings)
                header = next(rows, None)
                if not header:
                    continue
                headers = []
                for idx, cell in enumerate(header):
                    value = cell_content(cell.value, image_dict, sheet_drawings.get((cell.row, cell.column)))
                    headers.append(" " * (idx + 1) if value is None else self._escape_cell_content(value))
                lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(header)) + " |"]
                for row in rows:
                    values = merged_row_values(sheet, row, image_dict, sheet_drawings)
                    lines.append("| " + " | ".join(self._escape_cell_content(value) for value in values) + " |")
                if len(lines) > 2 or sheet_drawings:
                    tables.append(f"## {sheet.title}\n\n" + "\n".join(lines) + "\n\n\n")
            return "".join(tables)
        except Exception as e:
            maxkb_logger.error(f"excel split handle error: {e}")
            return f"error: {e}"

    def _escape_cell_content(self, cell_value):
        """转义单元格内容,避免破坏 Markdown 表格结构"""
        if cell_value is None:
            return ""

        cell_str = str(cell_value)

        # 替换换行符为 <br>
        cell_str = cell_str.replace("\n", "<br>")

        # 转义管道符 | 为 HTML 实体
        cell_str = cell_str.replace("|", "&#124;")

        # 如果内容包含反引号,需要转义
        if "`" in cell_str:
            cell_str = cell_str.replace("`", "&#96;")

        return cell_str

    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".xlsx"):
            return True
        return False
