# coding=utf-8
import logging

import xlrd

from common.handle.base_parse_table_handle import BaseParseTableHandle

max_kb = logging.getLogger("max_kb")


class XlsSplitHandle(BaseParseTableHandle):
    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        buffer = get_buffer(file)
        if file_name.endswith(".xls") and xlrd.inspect_format(content=buffer):
            return True
        return False

    def handle(self, file, get_buffer, save_image):
        buffer = get_buffer(file)
        try:
            wb = xlrd.open_workbook(file_contents=buffer)
            result = []
            sheets = wb.sheets()
            for sheet in sheets:
                paragraphs = []
                rows = iter([sheet.row_values(i) for i in range(sheet.nrows)])
                if not rows: continue
                ti = next(rows)
                last_line = {}
                for r in rows:
                    l = []
                    for i, c in enumerate(r):
                        if not c:
                            c = last_line[i]
                        else:
                            last_line[i] = c
                        t = str(ti[i]) if i < len(ti) else ""
                        t += (": " if t else "") + str(c)
                        l.append(t)
                    l = "; ".join(l)
                    if sheet.name.lower().find("sheet") < 0:
                        l += " ——" + sheet.name
                    paragraphs.append({'title': '', 'content': l})
                result.append({'name': sheet.name, 'paragraphs': paragraphs})

        except BaseException as e:
            max_kb.error(f'excel split handle error: {e}')
            return [{'name': file.name, 'paragraphs': []}]
        return result
