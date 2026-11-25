# coding=utf-8
import io
import traceback

from openpyxl import load_workbook

from common.handle.base_parse_table_handle import BaseParseTableHandle
from common.handle.impl.common_handle import validate_xlsx_buffer
from common.handle.impl.xlsx_utils import iter_sheet_content_rows, load_images, merged_row_values
from common.utils.logger import maxkb_logger


class XlsxParseTableHandle(BaseParseTableHandle):
    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".xlsx"):
            return True
        return False

    def fill_merged_cells(self, sheet, image_dict, drawings):
        data = []

        # 获取第一行作为标题行
        headers = []
        rows = iter_sheet_content_rows(sheet, drawings=drawings)
        try:
            title_row = next(rows)
        except StopIteration:
            return data
        for idx, cell in enumerate(title_row):
            if cell.value is None:
                headers.append(" " * (idx + 1))
            else:
                headers.append(cell.value)

        # 从第二行开始遍历每一行
        for row in rows:
            values = merged_row_values(sheet, row, image_dict, drawings)
            data.append({header: value if value is not None else "" for header, value in zip(headers, values)})
        return data

    def handle(self, file, get_buffer, save_image):
        buffer = get_buffer(file)
        try:
            validate_xlsx_buffer(io.BytesIO(buffer))
            wb = load_workbook(io.BytesIO(buffer))
            image_dict, drawings = load_images(io.BytesIO(buffer), wb, save_image)
            result = []
            for sheetname in wb.sheetnames:
                paragraphs = []
                ws = wb[sheetname]
                data = self.fill_merged_cells(ws, image_dict, drawings.get(sheetname, {}))

                for row in data:
                    row_output = "; ".join([f"{key}: {value}" for key, value in row.items()])
                    # print(row_output)
                    paragraphs.append({"title": "", "content": row_output})

                result.append({"name": sheetname, "paragraphs": paragraphs})

        except BaseException as e:
            maxkb_logger.error(f"Error processing XLSX file {file.name}: {e}, {traceback.format_exc()}")
            return [{"name": file.name, "paragraphs": []}]
        return result

    def get_content(self, file, save_image):
        try:
            # 加载 Excel 文件
            validate_xlsx_buffer(file)
            workbook = load_workbook(file)
            image_dict, drawings = load_images(file, workbook, save_image)
            md_tables = ""
            # 遍历所有工作表
            for sheetname in workbook.sheetnames:
                sheet = workbook[sheetname]
                rows = self.fill_merged_cells(sheet, image_dict, drawings.get(sheetname, {}))
                if len(rows) == 0:
                    continue

                # 添加 sheet 名称作为标题
                md_tables += f"## {sheetname}\n\n"

                # 提取表头和内容
                headers = [str(key).replace("|", "&#124;").replace("\n", "<br>") for key in rows[0]]

                # 构建 Markdown 表格
                md_table = "| " + " | ".join(headers) + " |\n"
                md_table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
                for row in rows:
                    cells = [str(value).replace("|", "&#124;").replace("\n", "<br>") for value in row.values()]
                    md_table += "| " + " | ".join(cells) + " |\n"

                md_tables += md_table + "\n\n"

            return md_tables
        except Exception as e:
            maxkb_logger.error(f"excel split handle error: {e}")
            return f"error: {e}"
