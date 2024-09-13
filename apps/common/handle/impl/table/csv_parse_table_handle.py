# coding=utf-8
import logging

from charset_normalizer import detect

from common.handle.base_parse_table_handle import BaseParseTableHandle

max_kb = logging.getLogger("max_kb")


class CsvSplitHandle(BaseParseTableHandle):
    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".csv"):
            return True
        return False

    def handle(self, file, get_buffer,save_image):
        buffer = get_buffer(file)
        try:
            content = buffer.decode(detect(buffer)['encoding'])
        except BaseException as e:
            max_kb.error(f'csv split handle error: {e}')
            return [{'name': file.name, 'paragraphs': []}]

        csv_model = content.split('\n')
        paragraphs = []
        # 第一行为标题
        title = csv_model[0].split(',')
        for row in csv_model[1:]:
            line = '; '.join([f'{key}:{value}' for key, value in zip(title, row.split(','))])
            paragraphs.append({'title': '', 'content': line})

        return [{'name': file.name, 'paragraphs': paragraphs}]
