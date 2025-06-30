# coding=utf-8
import logging
import traceback

from charset_normalizer import detect

from common.handle.base_parse_table_handle import BaseParseTableHandle
from common.utils.logger import maxkb_logger


class CsvParseTableHandle(BaseParseTableHandle):
    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".csv"):
            return True
        return False

    def handle(self, file, get_buffer, save_image):
        buffer = get_buffer(file)
        try:
            content = buffer.decode(detect(buffer)['encoding'])
        except BaseException as e:
            maxkb_logger.error(f"Error processing CSV file {file.name}: {e}, {traceback.format_exc()}")
            return [{'name': file.name, 'paragraphs': []}]

        csv_model = content.split('\n')
        paragraphs = []
        # 第一行为标题
        title = csv_model[0].split(',')
        for row in csv_model[1:]:
            if not row:
                continue
            line = '; '.join([f'{key}:{value}' for key, value in zip(title, row.split(','))])
            paragraphs.append({'title': '', 'content': line})

        return [{'name': file.name, 'paragraphs': paragraphs}]

    def get_content(self, file, save_image):
        buffer = file.read()
        try:
            return buffer.decode(detect(buffer)['encoding'])
        except BaseException as e:
            maxkb_logger.error(f'csv split handle error: {e}')
            return f'error: {e}'
